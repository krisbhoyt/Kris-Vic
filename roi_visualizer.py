import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Vic.ai branding colors
PRIMARY_COLOR = "#2E3B63"  # Dark Blue for Data
WHITE = "#FFFFFF"  # White background
BLACK = "#000000"  # Black for all text on charts (labels, titles, axes)

# Apply custom CSS for professional look
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {WHITE};
        padding: 20px;
    }}
    h1, h2, h3, h4 {{
        color: {PRIMARY_COLOR};  
        font-family: Arial, sans-serif;
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR}; 
        color: white;
        border-radius: 8px;
        font-size: 16px;
    }}
    .stMetric {{
        font-size: 20px;
        font-weight: bold;
    }}
    .stPlotlyChart {{
        padding-top: 10px;
    }}
    </style>
    """, unsafe_allow_html=True
)

# App title with branding colors
st.markdown(f"<h1 style='color:{PRIMARY_COLOR}; text-align: center;'>Vic.ai AP Automation ROI Tool</h1>", unsafe_allow_html=True)
st.write("This tool helps calculate the return on investment (ROI) for automating your Accounts Payable (AP) processes. Input your current metrics and projections to see potential savings.")

# Input fields for executive-level metrics
st.markdown("### Business Inputs")
with st.form(key="roi_form"):
    current_invoice_volume = st.number_input('Current Invoice Volume per Month', min_value=0, value=2000)
    growth_rate = st.number_input('Projected Growth Rate (%)', min_value=0.0, max_value=100.0, value=10.0)
    ap_processor_salary = st.number_input('AP Processor Salary ($)', min_value=0.0, value=50000.0)
    num_ap_processors = st.number_input('Number of AP Processors', min_value=0, value=3)
    missed_discounts = st.number_input('Missed Early Payer Discounts ($ per year)', min_value=0.0, value=20000.0)
    
    # Time to process one invoice before and after automation (in minutes)
    time_per_invoice_before = st.number_input('Time to Process One Invoice Before Automation (minutes)', min_value=0.0, value=60.0)
    time_per_invoice_after = st.number_input('Time to Process One Invoice After Automation (minutes)', min_value=0.0, value=30.0)
    
    # Automation rate
    automation_rate = st.number_input('Automation Rate (%)', min_value=0.0, max_value=100.0, value=70.0)

    automation_system_cost = st.number_input('AP Automation System Cost ($ per year)', min_value=0.0, value=20000.0)
    years = st.number_input('Number of Years for Projection', min_value=1, value=3)

    submit_button = st.form_submit_button(label="Calculate ROI")

if submit_button:
    # Function to calculate ROI with realistic scaling
    def calculate_roi_with_growth(current_invoice_volume, growth_rate, years, ap_processor_salary, num_ap_processors, 
                                  missed_discounts, time_per_invoice_before, time_per_invoice_after, 
                                  automation_system_cost, automation_rate):
        
        # Convert time from minutes to hours for the calculations
        time_per_invoice_before_hours = time_per_invoice_before / 60
        time_per_invoice_after_hours = time_per_invoice_after / 60

        # Calculate time saved per invoice
        time_saved_per_invoice_hours = time_per_invoice_before_hours - time_per_invoice_after_hours

        # Calculate the projected future invoice volume with realistic scaling
        growth_multiplier = (1 + growth_rate / 100) ** years
        annual_invoice_volume = current_invoice_volume * 12 * growth_multiplier  # Scaling to annual volume

        # Calculate total time saved per year, considering the automation rate
        total_time_saved_hours = time_saved_per_invoice_hours * annual_invoice_volume * (automation_rate / 100)

        # Assuming a standard work year (2,080 hours) per AP processor
        working_hours_per_year = 2080

        # Calculate the number of processors saved based on time saved
        processors_saved = total_time_saved_hours / working_hours_per_year

        # Ensure processors saved does not exceed the number of AP processors
        processors_saved = min(processors_saved, num_ap_processors)

        # Calculate labor cost savings based on time saved
        total_labor_cost_savings = processors_saved * ap_processor_salary

        # Early payer discount savings (realistic cap based on annual)
        early_payer_discount_savings = missed_discounts

        # Total savings (labor cost + early payer discounts)
        total_savings = total_labor_cost_savings + early_payer_discount_savings

        # Cumulative savings and investment over the years
        cumulative_savings = [total_savings * (year + 1) for year in range(years)]
        cumulative_investment = [automation_system_cost * (year + 1) for year in range(years)]
        roi_over_time = [(cumulative_savings[year] / cumulative_investment[year]) * 100 for year in range(years)]

        return {
            "Projected Invoice Volume": annual_invoice_volume,
            "Labor Cost Savings ($)": total_labor_cost_savings,
            "Early Payer Discount Savings ($)": early_payer_discount_savings,
            "Total Savings ($)": total_savings,
            "ROI (%)": roi_over_time[-1],
            "Processors Saved": processors_saved,
            "Cumulative Savings": cumulative_savings,
            "Cumulative Investment": cumulative_investment,
            "ROI Over Time": roi_over_time
        }

    # Calculate ROI with growth projection
    results = calculate_roi_with_growth(current_invoice_volume, growth_rate, years, ap_processor_salary, num_ap_processors, 
                                        missed_discounts, time_per_invoice_before, time_per_invoice_after, 
                                        automation_system_cost, automation_rate)

    # Display key metrics in a 3x2 grid for clarity
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Projected Invoice Volume", value=f"{int(results['Projected Invoice Volume']):,}")
    col1.metric(label="Labor Cost Savings ($)", value=f"${results['Labor Cost Savings ($)']:.2f}")
    col2.metric(label="Processors Saved", value=f"{results['Processors Saved']:.2f}")
    col2.metric(label="Early Payer Discount Savings ($)", value=f"${results['Early Payer Discount Savings ($)']:.2f}")
    col3.metric(label="Total Savings ($)", value=f"${results['Total Savings ($)']:.2f}")
    col3.metric(label="ROI (%)", value=f"{results['ROI (%)']:.2f}%")

    # Generate charts, each on its own line for better visibility
    st.markdown("### Visualization of Savings")

    # Chart 4: ROI Over 3 Years
    roi_fig = go.Figure()

    # Plot cumulative savings
    roi_fig.add_trace(go.Scatter(x=list(range(1, years + 1)), y=results['Cumulative Savings'],
                                 mode='lines+markers', name='Savings', marker_color=PRIMARY_COLOR))

    # Plot cumulative investment
    roi_fig.add_trace(go.Scatter(x=list(range(1, years + 1)), y=results['Cumulative Investment'],
                                 mode='lines+markers', name='Investment', marker_color='red'))

    roi_fig.update_layout(
        title='Cumulative Savings vs. Investment Over 3 Years',
        xaxis_title='Year',
        yaxis_title='Amount ($)',
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK),
        title_font=dict(size=16, color=BLACK),
        yaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        xaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        legend=dict(title_font=dict(color=BLACK), font=dict(color=BLACK))
    )
    st.plotly_chart(roi_fig, use_container_width=True)

    # Explanation of calculations
    st.markdown("### Explanation of Calculations")
    st.write(f"""
    **How We Calculate the ROI:**
    1. **Projected Invoice Volume**: We multiply the current monthly invoice volume by 12 to get the annual volume. Then, we apply the projected growth rate over {years} years.
    2. **Labor Cost Savings**: We calculate the total hours saved across all invoices, adjust it by the automation rate, and divide by the total annual working hours of a processor (2,080 hours). This gives us the number of processors saved, which is then multiplied by the processor's salary to calculate the labor cost savings.
    3. **Processors Saved**: This is calculated by dividing the total time saved (adjusted by the automation rate) by the annual working hours of a processor (2,080 hours).
    4. **Early Payer Discounts**: Savings come from capturing discounts that would otherwise be missed.
    5. **Total Savings**: This includes both labor cost savings and early payer discount savings.
    6. **ROI**: The total savings are compared to the annual cost of the AP automation system to calculate the ROI as a percentage.
    """)
