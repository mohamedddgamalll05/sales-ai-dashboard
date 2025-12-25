import base64
import io
import os
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

try:
    import seaborn as sns
    sns.set_style("whitegrid")
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("⚠️ Warning: seaborn not installed. Install with: pip install seaborn")

from database import dataset_col

# Use non-GUI backend for server-side rendering
matplotlib.use("Agg")
plt.rcParams["figure.facecolor"] = "#0a0a0a"  # Dark background to match theme
plt.rcParams["axes.facecolor"] = "#1a1a1a"  # Dark axes background
plt.rcParams["text.color"] = "#e5e7eb"  # Light text color
plt.rcParams["axes.labelcolor"] = "#e5e7eb"  # Light axis labels
plt.rcParams["xtick.color"] = "#9ca3af"  # Light tick colors
plt.rcParams["ytick.color"] = "#9ca3af"  # Light tick colors
plt.rcParams["axes.edgecolor"] = "#0d7377"  # Royal green axis edges
plt.rcParams["axes.labelcolor"] = "#e5e7eb"  # Light axis labels
plt.rcParams["axes.titlecolor"] = "#e5e7eb"  # Light titles

# Ensure outputs directory exists
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs" / "charts"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _figure_to_base64(fig, filename=None) -> str:
    """
    Convert matplotlib figure to base64 string for frontend display.
    Optionally save as PNG file for deliverables.
    """
    buf = io.BytesIO()
    # Increase DPI for sharper, larger text rendering - higher DPI for better quality
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    
    # Save PNG file for deliverables if filename provided
    if filename:
        filepath = OUTPUTS_DIR / filename
        fig.savefig(filepath, format="png", bbox_inches="tight", dpi=200)
    
    plt.close(fig)
    return encoded


def get_dashboard_data():
    """
    Compute high-level statistics with pandas and generate
    visualizations (bar chart + histogram) as base64 PNGs.
    """
    try:
        # Check connection first
        dataset_col.database.client.admin.command('ping')
        
        data = list(dataset_col.find({}, {"_id": 0}))
        if not data:
            print("⚠️ Warning: Dataset collection is empty. Please run ml/train_model.py or use /load-dataset endpoint.")
            return {
                "stats": {
                    "total_sales": 0,
                    "average_quantity": 0,
                    "median_quantity": 0,
                    "invoice_count": 0,
                    "category_frequencies": {},
                },
                "charts": {
                    "item_sales": None,
                    "amount_distribution": None,
                    "pie_chart": None,
                },
                "message": "Dataset collection is empty. Use /load-dataset endpoint to load data.",
            }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error fetching dataset: {e}")
        print(error_details)
        return {
            "stats": {
                "total_sales": 0,
                "average_quantity": 0,
                "median_quantity": 0,
                "invoice_count": 0,
                "category_frequencies": {},
            },
            "charts": {
                "item_sales": None,
                "amount_distribution": None,
                "pie_chart": None,
            },
            "error": str(e),
        }

    try:
        df = pd.DataFrame(data)
        if df.empty:
            print("⚠️ Warning: DataFrame is empty after conversion.")
            return {
                "stats": {
                    "total_sales": 0,
                    "average_quantity": 0,
                    "median_quantity": 0,
                    "invoice_count": 0,
                    "category_frequencies": {},
                },
                "charts": {
                    "item_sales": None,
                    "amount_distribution": None,
                    "pie_chart": None,
                },
            }
    except Exception as e:
        print(f"❌ Error creating DataFrame: {e}")
        return {
            "stats": {
                "total_sales": 0,
                "average_quantity": 0,
                "median_quantity": 0,
                "invoice_count": 0,
                "category_frequencies": {},
            },
            "charts": {
                "item_sales": None,
                "amount_distribution": None,
                "pie_chart": None,
            },
        }

    # ---- Normalize column names to be more robust to real dataset schema ----
    rename_map = {}
    if "Item" in df.columns and "item" not in df.columns:
        rename_map["Item"] = "item"
    if "Qty" in df.columns and "quantity" not in df.columns:
        rename_map["Qty"] = "quantity"
    if "Sales Price" in df.columns and "sales_price" not in df.columns:
        rename_map["Sales Price"] = "sales_price"
    if "Amount" in df.columns and "amount" not in df.columns:
        rename_map["Amount"] = "amount"

    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # Ensure required columns exist; otherwise provide safe defaults
    if "amount" not in df.columns and {"quantity", "sales_price"}.issubset(df.columns):
        df["amount"] = df["quantity"] * df["sales_price"]

    # Compute comprehensive statistics (matching PDF requirements)
    total_sales = float(df.get("amount", pd.Series([0])).sum())
    avg_quantity = float(df.get("quantity", pd.Series([0])).mean())
    median_quantity = float(df.get("quantity", pd.Series([0])).median())
    invoice_count = int(len(df))
    
    # Category frequencies (invoice_type value_counts equivalent)
    category_frequencies = {}
    if "invoice_type" in df.columns:
        category_frequencies = df["invoice_type"].value_counts().to_dict()
    elif "item" in df.columns:
        # Fallback to item categories
        category_frequencies = df["item"].value_counts().head(10).to_dict()

    # ---- Visual 1: Total sales by item (bar chart) ----
    item_sales_b64 = None
    group_dimension = None
    if {"item", "amount"}.issubset(df.columns):
        group_dimension = "item"
    elif {"invoice_type", "amount"}.issubset(df.columns):
        # graceful fallback if there is no "item" column
        group_dimension = "invoice_type"

    if group_dimension:
        grouped = (
            df.groupby(group_dimension)["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        # Create MUCH larger figure to fill space better with dark theme
        fig, ax = plt.subplots(figsize=(18, 10), facecolor="#0a0a0a")
        ax.set_facecolor("#1a1a1a")
        
        # Create more divergent color palette - royal green to teal/cyan spectrum
        # More divergent colors while staying in green theme
        divergent_colors = [
            '#0a5f63',      # Dark royal green
            '#0d7377',      # Primary royal green
            '#0f7a7e',      # Medium-dark
            '#118185',      # Medium
            '#13888c',      # Medium-light
            '#14b8a6',      # Accent teal-green
            '#16c4b3',      # Light teal
            '#1dd1c1',      # Bright teal
            '#26d0ce',      # Cyan-teal
            '#2dd4bf',      # Bright cyan-green
        ]
        # Make bars wider to fill more space
        bars = ax.bar(range(len(grouped)), grouped.values, 
                     color=divergent_colors[:len(grouped)], 
                     edgecolor="#14b8a6", linewidth=2, alpha=0.9, width=0.7)
        # Adjust layout to use full space
        plt.tight_layout(pad=2.0)
        ax.set_title("Top Items by Total Amount", fontsize=18, fontweight="bold", pad=20, color="#e5e7eb")
        ax.set_xlabel(group_dimension.replace("_", " ").title(), fontsize=15, color="#e5e7eb")
        ax.set_ylabel("Total Amount", fontsize=15, color="#e5e7eb")
        
        # Create labels with rank numbers - make them VERY visible with larger font
        ranked_labels = [f"#{i+1}\n{label}" for i, label in enumerate(grouped.index)]
        ax.set_xticks(range(len(grouped)))
        ax.set_xticklabels(ranked_labels, rotation=45, ha="right", fontsize=14, fontweight='bold', color="#e5e7eb")
        ax.grid(axis="y", alpha=0.2, linestyle="--", color="#0d7377")
        ax.spines['top'].set_color('#0d7377')
        ax.spines['bottom'].set_color('#0d7377')
        ax.spines['left'].set_color('#0d7377')
        ax.spines['right'].set_color('#0d7377')
        
        # Add value labels on bars with rank numbers - make them MUCH larger and prominent
        for i, bar in enumerate(bars):
            height = bar.get_height()
            # Show rank number prominently at the top
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.03,
                   f'#{i+1}',
                   ha='center', va='bottom', fontsize=16, fontweight='bold', 
                   color='#0a0a0a', bbox=dict(boxstyle='round,pad=0.3', facecolor='#14b8a6', alpha=0.9, edgecolor='#0d7377', linewidth=2))
            # Show value below rank number
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.10,
                   f'{height:,.0f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold', color='#e5e7eb')
        
        item_sales_b64 = _figure_to_base64(fig, "top_items_bar_chart.png")

    # ---- Visual 2: Distribution of invoice amounts (histogram) ----
    amount_dist_b64 = None
    if "amount" in df.columns:
        amounts = df["amount"].astype(float)
        if len(amounts) > 0:
            # Use log scale or clip outliers for better visualization
            upper = amounts.quantile(0.95)
            clipped = amounts.clip(upper=upper)

            # Create larger histogram to fill space better
            fig, ax = plt.subplots(figsize=(16, 8), facecolor="#0a0a0a")
            ax.set_facecolor("#1a1a1a")
            # Use gradient colors for histogram bars for more visual interest
            n, bins, patches = ax.hist(clipped, bins=30, edgecolor="#14b8a6", linewidth=1.5, alpha=0.85)
            # Color each bar with a gradient from dark to light royal green
            for i, patch in enumerate(patches):
                # Create gradient effect - darker at bottom, lighter at top
                gradient_factor = i / len(patches)
                r = int(10 + (13 - 10) * (1 - gradient_factor))
                g = int(95 + (115 - 95) * (1 - gradient_factor))
                b = int(99 + (119 - 99) * (1 - gradient_factor))
                patch.set_facecolor(f"#{r:02x}{g:02x}{b:02x}")
            ax.set_title("Distribution of Invoice Amounts (≤ 95th percentile)", fontsize=18, fontweight="bold", pad=20, color="#e5e7eb")
            ax.set_xlabel("Amount", fontsize=15, color="#e5e7eb")
            ax.set_ylabel("Frequency", fontsize=15, color="#e5e7eb")
            ax.grid(axis="y", alpha=0.2, linestyle="--", color="#0d7377")
            ax.spines['top'].set_color('#0d7377')
            ax.spines['bottom'].set_color('#0d7377')
            ax.spines['left'].set_color('#0d7377')
            ax.spines['right'].set_color('#0d7377')
            
            # Adjust layout to use full space
            plt.tight_layout(pad=2.0)
            
            # Add median line in royal green
            median_val = amounts.median()
            if median_val <= upper:
                ax.axvline(median_val, color="#14b8a6", linestyle="--", linewidth=2, label=f"Median: {median_val:,.0f}")
                legend = ax.legend(facecolor="#1a1a1a", edgecolor="#0d7377", labelcolor="#e5e7eb")
                legend.get_frame().set_alpha(0.9)
            
            amount_dist_b64 = _figure_to_base64(fig, "amount_distribution_histogram.png")

    # ---- Visual 3: Pie Chart - Category Frequencies (PDF Requirement) ----
    pie_chart_b64 = None
    if category_frequencies and len(category_frequencies) > 0:
        # Take top 8 categories for pie chart readability
        top_categories = dict(list(category_frequencies.items())[:8])
        labels = list(top_categories.keys())
        sizes = list(top_categories.values())
        
        # Truncate long labels to prevent overlap - but keep more characters for larger legend
        max_label_length = 25  # Increased from 15 to 25 for larger legend
        display_labels = [label[:max_label_length] + ('...' if len(label) > max_label_length else '') for label in labels]
        
        # Create more divergent royal green color palette - wider spectrum
        # More divergent colors from dark green through teal to cyan-green
        divergent_palette = [
            (10, 95, 99),      # #0a5f63 - Dark royal green
            (13, 115, 119),    # #0d7377 - Primary royal green
            (16, 125, 129),    # #107d81 - Medium-dark
            (20, 138, 142),    # #148a8e - Medium
            (23, 150, 154),    # #17969a - Medium-light
            (20, 184, 166),    # #14b8a6 - Accent teal-green
            (22, 196, 179),    # #16c4b3 - Light teal
            (29, 209, 193),    # #1dd1c1 - Bright teal
            (38, 208, 206),    # #26d0ce - Cyan-teal
            (45, 212, 191),    # #2dd4bf - Bright cyan-green
        ]
        # Convert to matplotlib colors (normalized 0-1)
        colors = [(r/255, g/255, b/255) for r, g, b in divergent_palette[:len(labels)]]
        # If we need more colors, cycle through the palette with variation
        if len(colors) < len(labels):
            while len(colors) < len(labels):
                idx = len(colors) % len(divergent_palette)
                colors.append((divergent_palette[idx][0]/255, divergent_palette[idx][1]/255, divergent_palette[idx][2]/255))
        
        # Create ULTRA LARGE figure to fill space - even bigger with dark theme
        fig, ax = plt.subplots(figsize=(22, 18), facecolor="#0a0a0a")
        ax.set_facecolor("#0a0a0a")
        
        # Create pie chart with ULTRA LARGE text - make it very visible
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=None,  # Don't show labels on pie slices to avoid overlap
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            pctdistance=0.68,  # Move percentage text inward for larger text
            textprops={'fontsize': 24, 'fontweight': 'bold', 'color': '#0a0a0a'}  # Dark text for visibility on green
        )
        
        ax.set_title("Invoice Type Distribution", fontsize=26, fontweight="bold", pad=30, color="#e5e7eb")
        
        # Add legend outside the pie chart with ULTRA LARGE font size - make it very visible
        legend = ax.legend(
            wedges, 
            display_labels,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1.2, 0, 0.5, 1),  # Move further right for more space
            fontsize=28,  # ULTRA LARGE - 28 for maximum visibility and compatibility with pie size
            title_fontsize=32,  # Even larger title - 32
            frameon=True,
            fancybox=True,
            shadow=True,
            prop={'weight': 'bold', 'size': 28}  # Make all legend text bold and ULTRA large
        )
        # Make legend frame more visible with royal green theme
        legend.get_frame().set_alpha(0.95)
        legend.get_frame().set_facecolor('#1a1a1a')
        legend.get_frame().set_edgecolor('#0d7377')
        legend.get_frame().set_linewidth(3)
        # Update legend text colors
        for text in legend.get_texts():
            text.set_color('#e5e7eb')
        legend.get_title().set_color('#14b8a6')
        
        # Improve text readability for percentage labels - make them ULTRA LARGE
        for autotext in autotexts:
            autotext.set_color('#0a0a0a')  # Dark text on light green slices
            autotext.set_fontweight('bold')
            autotext.set_fontsize(24)  # ULTRA LARGE - 24 for maximum visibility
        
        # Adjust layout to use full space and prevent clipping
        plt.tight_layout(pad=3.0)
        
        pie_chart_b64 = _figure_to_base64(fig, "category_frequencies_pie_chart.png")

    return {
        "stats": {
            "total_sales": total_sales,
            "average_quantity": avg_quantity,
            "median_quantity": median_quantity,
            "invoice_count": invoice_count,
            "category_frequencies": category_frequencies,
        },
        "charts": {
            "item_sales": item_sales_b64,
            "amount_distribution": amount_dist_b64,
            "pie_chart": pie_chart_b64,
        },
    }
