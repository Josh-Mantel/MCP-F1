#!/usr/bin/env python3
"""
F1 MCP Server - Formula 1 data provider using FastF1
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import fastf1
import pandas as pd
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("f1-mcp-server")

# Configure FastF1 cache
import os
cache_dir = "cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    logger.info(f"Created cache directory: {cache_dir}")

try:
    fastf1.Cache.enable_cache(cache_dir)
    logger.info(f"FastF1 cache enabled at: {cache_dir}")
except Exception as e:
    logger.warning(f"Failed to enable FastF1 cache: {e}")
    logger.info("Continuing without cache - data will be fetched fresh each time")

app = Server("f1-mcp-server")


class F1SessionRequest(BaseModel):
    """Request model for F1 session data."""

    year: int = Field(..., description="Season year (e.g., 2024)")
    round_number: Optional[int] = Field(None, description="Round number (1-24)")
    event_name: Optional[str] = Field(
        None, description="Event name (e.g., 'Monaco Grand Prix')"
    )
    session: str = Field(..., description="Session type: 'FP1', 'FP2', 'FP3', 'Q', 'R'")


class F1StandingsRequest(BaseModel):
    """Request model for F1 standings."""

    year: int = Field(..., description="Season year (e.g., 2024)")
    round_number: Optional[int] = Field(
        None, description="Round number (after which round)"
    )


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available F1 data tools."""
    return [
        Tool(
            name="get_race_schedule",
            description="Get the race schedule for a specific F1 season",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Season year (e.g., 2024)",
                        "minimum": 1950,
                        "maximum": 2030,
                    }
                },
                "required": ["year"],
            },
        ),
        Tool(
            name="get_session_results",
            description="Get results for a specific F1 session (practice, qualifying, or race)",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Season year (e.g., 2024)",
                    },
                    "round_number": {
                        "type": "integer",
                        "description": "Round number (1-24)",
                        "minimum": 1,
                        "maximum": 24,
                    },
                    "session": {
                        "type": "string",
                        "description": "Session type",
                        "enum": ["FP1", "FP2", "FP3", "Q", "R"],
                    },
                },
                "required": ["year", "round_number", "session"],
            },
        ),
        Tool(
            name="get_driver_standings",
            description="Get driver championship standings for a season",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Season year (e.g., 2024)",
                    },
                    "round_number": {
                        "type": "integer",
                        "description": "Round number (optional, gets standings after this round)",
                        "minimum": 1,
                        "maximum": 24,
                    },
                },
                "required": ["year"],
            },
        ),
        Tool(
            name="get_constructor_standings",
            description="Get constructor championship standings for a season",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Season year (e.g., 2024)",
                    },
                    "round_number": {
                        "type": "integer",
                        "description": "Round number (optional, gets standings after this round)",
                        "minimum": 1,
                        "maximum": 24,
                    },
                },
                "required": ["year"],
            },
        ),
        Tool(
            name="get_lap_times",
            description="Get lap times for a specific session",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "Season year (e.g., 2024)",
                    },
                    "round_number": {
                        "type": "integer",
                        "description": "Round number (1-24)",
                    },
                    "session": {
                        "type": "string",
                        "description": "Session type",
                        "enum": ["FP1", "FP2", "FP3", "Q", "R"],
                    },
                    "driver": {
                        "type": "string",
                        "description": "Driver abbreviation (optional, e.g., 'VER', 'HAM')",
                    },
                },
                "required": ["year", "round_number", "session"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for F1 data."""
    try:
        if name == "get_race_schedule":
            return await get_race_schedule(arguments)
        elif name == "get_session_results":
            return await get_session_results(arguments)
        elif name == "get_driver_standings":
            return await get_driver_standings(arguments)
        elif name == "get_constructor_standings":
            return await get_constructor_standings(arguments)
        elif name == "get_lap_times":
            return await get_lap_times(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_race_schedule(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get race schedule for a season."""
    year = arguments["year"]

    try:
        schedule = fastf1.get_event_schedule(year)

        # Convert to a more readable format
        schedule_data = []
        for _, event in schedule.iterrows():
            schedule_data.append(
                {
                    "round": (
                        int(event["RoundNumber"])
                        if pd.notna(event["RoundNumber"])
                        else None
                    ),
                    "event_name": event["EventName"],
                    "location": event["Location"],
                    "country": event["Country"],
                    "event_date": (
                        event["EventDate"].strftime("%Y-%m-%d")
                        if pd.notna(event["EventDate"])
                        else None
                    ),
                    "event_format": (
                        event["EventFormat"]
                        if "EventFormat" in event
                        else "Conventional"
                    ),
                }
            )

        result = {
            "season": year,
            "total_rounds": len(schedule_data),
            "events": schedule_data,
        }

        return [
            TextContent(
                type="text",
                text=f"F1 {year} Race Schedule:\n\n" + json.dumps(result, indent=2),
            )
        ]

    except Exception as e:
        return [
            TextContent(
                type="text", text=f"Error getting schedule for {year}: {str(e)}"
            )
        ]


async def get_session_results(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get session results."""
    year = arguments["year"]
    round_number = arguments["round_number"]
    session_type = arguments["session"]

    try:
        session = fastf1.get_session(year, round_number, session_type)
        session.load()

        results = session.results

        # Convert results to readable format
        results_data = []
        for _, driver in results.iterrows():
            results_data.append(
                {
                    "position": (
                        int(driver["Position"])
                        if pd.notna(driver["Position"])
                        else None
                    ),
                    "driver_number": (
                        int(driver["DriverNumber"])
                        if pd.notna(driver["DriverNumber"])
                        else None
                    ),
                    "driver": driver["Abbreviation"],
                    "full_name": driver["FullName"],
                    "team": driver["TeamName"],
                    "time": str(driver["Time"]) if pd.notna(driver["Time"]) else None,
                    "status": driver["Status"] if "Status" in driver else None,
                    "points": (
                        float(driver["Points"])
                        if pd.notna(driver.get("Points", 0))
                        else 0
                    ),
                }
            )

        result = {
            "year": year,
            "round": round_number,
            "session": session_type,
            "event_name": session.event["EventName"],
            "location": session.event["Location"],
            "results": results_data,
        }

        return [
            TextContent(
                type="text",
                text=f"F1 {year} Round {round_number} {session_type} Results:\n\n"
                + json.dumps(result, indent=2),
            )
        ]

    except Exception as e:
        return [
            TextContent(type="text", text=f"Error getting session results: {str(e)}")
        ]


async def get_driver_standings(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get driver championship standings."""
    year = arguments["year"]
    round_number = arguments.get("round_number")

    try:
        # Get the schedule to determine which round to use
        schedule = fastf1.get_event_schedule(year)

        if round_number is None:
            # Get latest completed round
            current_date = datetime.now()
            completed_rounds = schedule[schedule["EventDate"] <= current_date]
            if completed_rounds.empty:
                round_number = 1
            else:
                round_number = int(completed_rounds["RoundNumber"].max())

        # Get race session for standings calculation
        session = fastf1.get_session(year, round_number, "R")
        session.load()

        # Calculate standings (simplified - in real implementation you'd sum points across all rounds)
        results = session.results
        standings_data = []

        for _, driver in results.iterrows():
            standings_data.append(
                {
                    "position": (
                        int(driver["Position"])
                        if pd.notna(driver["Position"])
                        else None
                    ),
                    "driver": driver["Abbreviation"],
                    "full_name": driver["FullName"],
                    "team": driver["TeamName"],
                    "points": (
                        float(driver["Points"])
                        if pd.notna(driver.get("Points", 0))
                        else 0
                    ),
                }
            )

        # Sort by points (descending)
        standings_data.sort(key=lambda x: x["points"] or 0, reverse=True)

        result = {
            "year": year,
            "after_round": round_number,
            "standings": standings_data,
        }

        return [
            TextContent(
                type="text",
                text=f"F1 {year} Driver Standings (after Round {round_number}):\n\n"
                + json.dumps(result, indent=2),
            )
        ]

    except Exception as e:
        return [
            TextContent(type="text", text=f"Error getting driver standings: {str(e)}")
        ]


async def get_constructor_standings(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get constructor championship standings."""
    year = arguments["year"]
    round_number = arguments.get("round_number")

    try:
        # Get the schedule to determine which round to use
        schedule = fastf1.get_event_schedule(year)

        if round_number is None:
            # Get latest completed round
            current_date = datetime.now()
            completed_rounds = schedule[schedule["EventDate"] <= current_date]
            if completed_rounds.empty:
                round_number = 1
            else:
                round_number = int(completed_rounds["RoundNumber"].max())

        # Get race session for standings calculation
        session = fastf1.get_session(year, round_number, "R")
        session.load()

        results = session.results

        # Group by team and sum points
        team_points = {}
        for _, driver in results.iterrows():
            team = driver["TeamName"]
            points = float(driver["Points"]) if pd.notna(driver.get("Points", 0)) else 0

            if team not in team_points:
                team_points[team] = {"points": 0, "drivers": []}

            team_points[team]["points"] += points
            team_points[team]["drivers"].append(
                {
                    "name": driver["FullName"],
                    "abbreviation": driver["Abbreviation"],
                    "points": points,
                }
            )

        # Convert to list and sort
        standings_data = []
        for position, (team, data) in enumerate(
            sorted(team_points.items(), key=lambda x: x[1]["points"], reverse=True), 1
        ):
            standings_data.append(
                {
                    "position": position,
                    "team": team,
                    "points": data["points"],
                    "drivers": data["drivers"],
                }
            )

        result = {
            "year": year,
            "after_round": round_number,
            "standings": standings_data,
        }

        return [
            TextContent(
                type="text",
                text=f"F1 {year} Constructor Standings (after Round {round_number}):\n\n"
                + json.dumps(result, indent=2),
            )
        ]

    except Exception as e:
        return [
            TextContent(
                type="text", text=f"Error getting constructor standings: {str(e)}"
            )
        ]


async def get_lap_times(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get lap times for a session."""
    year = arguments["year"]
    round_number = arguments["round_number"]
    session_type = arguments["session"]
    driver_filter = arguments.get("driver")

    try:
        session = fastf1.get_session(year, round_number, session_type)
        session.load()

        laps = session.laps

        # Filter by driver if specified
        if driver_filter:
            laps = laps[laps["Driver"] == driver_filter.upper()]

        # Convert lap times to readable format
        lap_data = []
        for _, lap in laps.iterrows():
            lap_data.append(
                {
                    "lap_number": (
                        int(lap["LapNumber"]) if pd.notna(lap["LapNumber"]) else None
                    ),
                    "driver": lap["Driver"],
                    "team": lap["Team"],
                    "lap_time": (
                        str(lap["LapTime"]) if pd.notna(lap["LapTime"]) else None
                    ),
                    "sector_1": (
                        str(lap["Sector1Time"])
                        if pd.notna(lap.get("Sector1Time"))
                        else None
                    ),
                    "sector_2": (
                        str(lap["Sector2Time"])
                        if pd.notna(lap.get("Sector2Time"))
                        else None
                    ),
                    "sector_3": (
                        str(lap["Sector3Time"])
                        if pd.notna(lap.get("Sector3Time"))
                        else None
                    ),
                    "compound": lap.get("Compound", "Unknown"),
                    "tyre_life": (
                        int(lap["TyreLife"]) if pd.notna(lap.get("TyreLife")) else None
                    ),
                }
            )

        result = {
            "year": year,
            "round": round_number,
            "session": session_type,
            "event_name": session.event["EventName"],
            "driver_filter": driver_filter,
            "total_laps": len(lap_data),
            "laps": lap_data[:50],  # Limit to first 50 laps for readability
        }

        if len(lap_data) > 50:
            result["note"] = f"Showing first 50 of {len(lap_data)} laps"

        return [
            TextContent(
                type="text",
                text=f"F1 {year} Round {round_number} {session_type} Lap Times:\n\n"
                + json.dumps(result, indent=2),
            )
        ]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting lap times: {str(e)}")]


async def main():
    """Main entry point for the server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
