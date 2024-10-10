import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Vic.ai branding colors
PRIMARY_COLOR = "#2E3B63"  # Dark Blue for Data
WHITE = "#FFFFFF"  # White background
BLACK = "#000000"  # Black for all text on charts (labels, titles, axes)

# Apply custom CSS for professional look
st.markdown(
    f'''
    <style>
    .reportview-container {{
        background-color: {WHITE};
        padding: 20px;
    }}
    h1, h2, h3, h4 {{
        color: {WHITE};  
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
    ''', unsafe_allow_html=True
)

# App title with branding colors
st.markdown(f"<h1 style='color:{WHITE}; text-align: center;'>Vic.ai AP Automation ROI Tool</h1>", unsafe_allow_html=True)
st.write("This tool helps calculate the return on investment (ROI) for automating your Accounts Payable (AP) processes. Input your current metrics and projections to see potential savings.")

# Input fields for executive-level metrics
st.markdown("### Key Metrics")
with st.form(key="roi_form"):
    current_invoice_volume = st.number_input('Current Invoice Volume per Month', min_value=0, value=5000)
    growth_rate = st.number_input('Projected Growth Rate (%)', min_value=0, max_value=100, value=2)
    ap_processor_salary = st.number_input('AP Processor Salary ($)', min_value=0.00, value=55000.00)
    num_ap_processors = st.number_input('Number of AP Processors', min_value=0, value=5)
    missed_discounts = st.number_input('Missed Early Payer Discounts ($ per year)', min_value=0.00, value=25000.00)
    
    # Time to process one invoice before and after automation (in minutes)
    time_per_invoice_before = st.number_input('Time to Process One Invoice Before Automation (minutes)', min_value=0.0, value=8.0)
    time_per_invoice_after = st.number_input('Time to Process One Invoice After Automation (minutes)', min_value=0.0, value=1.5)
    
    # Automation rate
    automation_rate = st.number_input('Automation Rate (%)', min_value=0, max_value=100, value=70)

    automation_system_cost = st.number_input('AP Automation System Cost ($ per year)', min_value=0.0, value=120000.0)
    years = st.number_input('Number of Years for Projection', min_value=1, value=3)

    submit_button = st.form_submit_button(label="Calculate ROI")

if submit_button:
    def calculate_roi_with_growth(current_invoice_volume, growth_rate, years, ap_processor_salary, num_ap_processors, 
                                  missed_discounts, time_per_invoice_before, time_per_invoice_after, 
                                  automation_system_cost, automation_rate):
        
        # Calculate the projected future invoice volume with realistic scaling
        growth_multiplier = (1 + growth_rate / 100) ** years
        annual_invoice_volume = current_invoice_volume * 12 * growth_multiplier  # Scaling to annual volume

        # Convert time from minutes to hours for the calculations
        time_per_invoice_before_hours = time_per_invoice_before / 60
        time_per_invoice_after_hours = time_per_invoice_after / 60

        # Define an inverted exponential curve for progressive automation
        def exponential_progression_inverted(target_rate, years, lambd=0.7):
            # Invert the exponential progression so that it starts at 0 and approaches the target rate
            return [target_rate * (1 - np.exp(-lambd * t)) for t in range(0, years + 1)]

        # Use inverted exponential progression to calculate the automation rate over the years
        automation_rates = exponential_progression_inverted(automation_rate / 100, years)

        # Initialize list to store time spent each year
        time_spent_years = []

        # Loop through the automation rates for each year and calculate time spent
        for rate in automation_rates:
            # Start with maximum manual processing and reduce as automation progresses
            non_automated_invoice_volume = annual_invoice_volume * (1 - rate)
            # Calculate the average time spent per invoice (combination of automated and non-automated)
            avg_time_per_invoice_year = ((non_automated_invoice_volume * time_per_invoice_after_hours) + 
                                         (annual_invoice_volume * rate * time_per_invoice_before_hours)) / annual_invoice_volume
            time_per_invoice_years.append(avg_time_per_invoice_year)

        # Calculate the time per invoice before automation (Year 0)
        avg_time_before_automation = time_per_invoice_before_hours
        time_per_invoice_years = [avg_time_before_automation] + time_per_invoice_years

        # Calculate total time spent on non-automated invoices after automation
        total_time_after_hours = (annual_invoice_volume * (1 - automation_rate / 100)) * time_per_invoice_after_hours

        # Total time saved is the difference between total time spent before and after automation
        total_time_saved_hours = total_time_before_hours - total_time_after_hours

        # Assuming a standard work year (2,080 hours) per AP processor
        working_hours_per_year = 2080

        # Calculate total workload in hours for all processors
        total_workload_before = num_ap_processors * working_hours_per_year

        # Calculate how much of the total workload is reduced by automation
        workload_reduced_by_automation = total_workload_before * (automation_rate / 100)

        # Calculate processors saved based on workload reduction
        processors_saved = workload_reduced_by_automation / working_hours_per_year

        # Ensure processors saved doesn't exceed the current number of AP processors
        processors_saved = min(processors_saved, num_ap_processors)

        # Calculate labor cost savings based on processors saved
        total_labor_cost_savings = processors_saved * ap_processor_salary

        # Define non-automated invoice volume for future use
        non_automated_invoice_volume = current_invoice_volume * (1 - automation_rate / 100)

        # Prevent division by zero or negative value when calculating invoices per processor after automation
        remaining_processors = num_ap_processors - processors_saved

        if remaining_processors > 0:
            invoices_per_processor_after = non_automated_invoice_volume / remaining_processors
        else:
            invoices_per_processor_after = 0  # Set to 0 or another meaningful value if all processors are saved

        # Early payer discount savings (realistic cap based on annual)
        early_payer_discount_savings = missed_discounts

        # Total savings (labor cost + early payer discounts)
        total_savings = total_labor_cost_savings + (early_payer_discount_savings * years)

        # Cumulative savings and investment over the years
        cumulative_savings = [total_savings * (year + 1) for year in range(years)]
        cumulative_investment = [automation_system_cost * (year + 1) for year in range(years)]

        # Calculate net savings (savings - investment)
        net_savings = [cumulative_savings[year] - cumulative_investment[year] for year in range(years)]

        # Calculate ROI (%) for each year based on the cumulative savings and cumulative investment
        roi_over_time = [(cumulative_savings[year] / cumulative_investment[year]) * 100 if cumulative_investment[year] != 0 else 0 for year in range(years)]

        # Ensure the ROI for the final year is added to the results
        roi_final = roi_over_time[-1]

        # Time Efficiency Gains
        time_saved_per_invoice = time_per_invoice_before - time_per_invoice_after
        total_time_saved = time_saved_per_invoice * current_invoice_volume * (automation_rate / 100)

        # Processor Productivity Gains
        invoices_per_processor_before = current_invoice_volume / num_ap_processors
        invoices_per_processor_after = non_automated_invoice_volume / remaining_processors if remaining_processors > 0 else 0

        total_hours_saved = (total_time_saved / 60)
        

        # Return results
        return {
            "Projected Invoice Volume": annual_invoice_volume,
            "Labor Cost Savings ($)": total_labor_cost_savings,
            "Early Payer Discount Savings ($)": early_payer_discount_savings,
            "Total Savings ($)": total_savings,
            "Net Savings": net_savings,
            "Processors Saved": processors_saved,
            "Time Efficiency Gain": total_time_saved,
            "Processor Productivity Gains": invoices_per_processor_after,
            "Time Spent Over 3 Years (hours)": time_spent_years,
            "ROI (%)": roi_final,
            "ROI Over Time": roi_over_time,
            "Hours Saved": total_hours_saved,
            "Cumulative Savings": cumulative_savings,
            "Cumulative Investment": cumulative_investment,
            "Automation Rates Over Time": automation_rates,
            "Processing Time Per Invoice (hours)": time_per_invoice_years
        }

    # Calculate ROI with growth projection
    results = calculate_roi_with_growth(current_invoice_volume, growth_rate, years, ap_processor_salary, num_ap_processors, 
                                        missed_discounts, time_per_invoice_before, time_per_invoice_after, 
                                        automation_system_cost, automation_rate)

    # Display Efficiency Metrics
    st.markdown("### Efficiency Gains")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Hours Saved", value=f"{int(results['Hours Saved']):,}")
    col2.metric(label="Invoices / Processor (Year)", value=f"{int(results['Processor Productivity Gains']):.2f}")

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

    # Chart 1: ROI Over 3 Years
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

    # Chart: Time Spent Over 3 Years with Exponential Automation
    time_spent_fig = go.Figure()

    # Years for the x-axis (including Year 0)
    years_list = ['Year 0'] + [f'Year {i}' for i in range(1, years + 1)]

    # Time spent over 3 years should now correctly incorporate the exponential progression of automation
    time_spent_fig.add_trace(go.Scatter(
        x=years_list,
        y=results['Processing Time Per Invoice (hours)'],  # Data reflects exponential progression of automation
        mode='lines+markers', 
        name='Time Spent (hours)',
        line=dict(color=PRIMARY_COLOR)
    ))

    # Update layout for the chart
    time_spent_fig.update_layout(
        title=dict(
            text='Invoice Processing Time',
            font=dict(size=16, color=BLACK)
        ),
        xaxis_title='Year',
        yaxis_title='Time Spent (hours)',
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK),
        yaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        xaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        legend=dict(title_font=dict(color=BLACK), font=dict(color=BLACK))
    )

    # Display the chart in Streamlit
    st.plotly_chart(time_spent_fig, use_container_width=True)

    # Chart 3: Net Savings Over 3 Years
    net_savings_fig = go.Figure()

    # Plot net savings
    net_savings_fig.add_trace(go.Scatter(x=list(range(1, years + 1)), y=results['Net Savings'],
                                         mode='lines+markers', name='Net Savings', marker_color=PRIMARY_COLOR))

    net_savings_fig.update_layout(
        title='Net Savings Over 3 Years',
        xaxis_title='Year',
        yaxis_title='Net Savings ($)',
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK),
        title_font=dict(size=16, color=BLACK),
        yaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        xaxis=dict(title_font=dict(color=BLACK), tickfont=dict(color=BLACK)),
        legend=dict(title_font=dict(color=BLACK), font=dict(color=BLACK))
    )

    st.plotly_chart(net_savings_fig, use_container_width=True)

    # Explanation of calculations
    st.markdown("### Explanation of Calculations")
    st.write(f'''
    **How We Calculate the ROI:**
    1. **Projected Invoice Volume**: We multiply the current monthly invoice volume by 12 to get the annual volume. Then, we apply the projected growth rate over {years} years.
    2. **Labor Cost Savings**: We calculate the total hours saved across all invoices, adjust it by the automation rate, and divide by the total annual working hours of a processor (2,080 hours). This gives us the number of processors saved, which is then multiplied by the processor's salary to calculate the labor cost savings.
    3. **Processors Saved**: This is calculated by dividing the total time saved (adjusted by the automation rate) by the annual working hours of a processor (2,080 hours).
    4. **Early Payer Discounts**: Savings come from capturing discounts that would otherwise be missed.
    5. **Total Savings**: This includes both labor cost savings and early payer discount savings.
    6. **ROI**: The total savings are compared to the annual cost of the AP automation system to calculate the ROI as a percentage.
    ''')
