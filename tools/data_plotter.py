"""
Data Plotter Tool
Creates simple data visualizations using matplotlib.
"""

import matplotlib.pyplot as plt
import io
import base64
import json
import logging
import os
from typing import Dict, Any, List, Tuple

class DataPlotter:
    """Tool for creating data visualizations."""

    def __init__(self):
        """Initialize the data plotter."""
        self.output_dir = "output"
        self.logger = logging.getLogger(__name__)

        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_bar_chart(self, data: Dict[str, float], title: str = "Bar Chart") -> str:
        """
        Create a bar chart from data.

        Args:
            data (Dict[str, float]): Data for the chart
            title (str): Chart title

        Returns:
            str: Path to the generated chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            categories = list(data.keys())
            values = list(data.values())

            ax.bar(categories, values, color='skyblue', edgecolor='navy')

            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel('Categories', fontsize=12)
            ax.set_ylabel('Values', fontsize=12)

            # Rotate x-axis labels if they are long
            if len(max(categories, key=len)) > 10:
                plt.xticks(rotation=45, ha='right')

            plt.tight_layout()

            # Save the plot
            filename = f"bar_chart_{len(categories)}_{title.replace(' ', '_').lower()}.png"
            filepath = os.path.join(self.output_dir, filename)

            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating bar chart: {e}")
            return ""

    def create_line_chart(self, data: List[Tuple[str, float]], title: str = "Line Chart") -> str:
        """
        Create a line chart from data.

        Args:
            data (List[Tuple[str, float]]): Data points for the chart
            title (str): Chart title

        Returns:
            str: Path to the generated chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            x_values = [point[0] for point in data]
            y_values = [point[1] for point in data]

            ax.plot(x_values, y_values, marker='o', linewidth=2, markersize=6)

            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel('X-axis', fontsize=12)
            ax.set_ylabel('Y-axis', fontsize=12)

            # Add grid for better readability
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save the plot
            filename = f"line_chart_{len(data)}_{title.replace(' ', '_').lower()}.png"
            filepath = os.path.join(self.output_dir, filename)

            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating line chart: {e}")
            return ""

    def create_pie_chart(self, data: Dict[str, float], title: str = "Pie Chart") -> str:
        """
        Create a pie chart from data.

        Args:
            data (Dict[str, float]): Data for the chart
            title (str): Chart title

        Returns:
            str: Path to the generated chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(8, 8))

            labels = list(data.keys())
            sizes = list(data.values())

            # Create pie chart with percentages
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                             startangle=90, colors=plt.cm.Set3.colors)

            ax.set_title(title, fontsize=16, fontweight='bold')

            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')

            plt.tight_layout()

            # Save the plot
            filename = f"pie_chart_{len(data)}_{title.replace(' ', '_').lower()}.png"
            filepath = os.path.join(self.output_dir, filename)

            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating pie chart: {e}")
            return ""

    def run(self, data_input: str, chart_type: str = "bar", title: str = "Data Visualization") -> str:
        """
        Main method to run the data plotter tool.

        Args:
            data_input (str): JSON string containing data for plotting
            chart_type (str): Type of chart to create (bar, line, pie)
            title (str): Chart title

        Returns:
            str: Path to the generated chart image or error message
        """
        try:
            # Parse the data input
            try:
                data = json.loads(data_input)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a simple default visualization
                self.logger.warning(f"Invalid JSON input, using default data. Input was: {data_input[:100]}")
                data = {"Data Point 1": 30, "Data Point 2": 45, "Data Point 3": 25}
                title = "Sample Data Visualization"

            # Ensure data is a dict for bar/pie charts
            if not isinstance(data, dict):
                self.logger.warning(f"Data is not a dict, converting. Type: {type(data)}")
                if isinstance(data, list):
                    data = {f"Item {i+1}": val if isinstance(val, (int, float)) else i+1 for i, val in enumerate(data)}
                else:
                    data = {"Sample": 100}

            if chart_type.lower() == "bar":
                filepath = self.create_bar_chart(data, title)
            elif chart_type.lower() == "line":
                # Convert dict to list of tuples for line chart
                line_data = [(k, v) for k, v in data.items()]
                filepath = self.create_line_chart(line_data, title)
            elif chart_type.lower() == "pie":
                filepath = self.create_pie_chart(data, title)
            else:
                return f"Error: Unsupported chart type '{chart_type}'. Supported types: bar, line, pie"

            if filepath:
                return f"Chart successfully created: {filepath}"
            else:
                return "Error: Failed to create chart"

        except Exception as e:
            self.logger.error(f"Unexpected error in data plotter: {e}")
            return f"Error: {str(e)}"


def data_plotter_tool(data_input: str, chart_type: str = "bar", title: str = "Data Visualization") -> str:
    """
    Standalone function for data plotter tool.

    Args:
        data_input (str): JSON string containing data for plotting
        chart_type (str): Type of chart to create (bar, line, pie)
        title (str): Chart title

    Returns:
        str: Path to the generated chart image or error message
    """
    plotter = DataPlotter()
    return plotter.run(data_input, chart_type, title)
