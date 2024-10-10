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
    initial_time_per_invoice = st.number_input('Initial Time to Process One Invoice (minutes)', min_value=0.0, value=8.0)
    time_per_invoice_after = st.number_input('Time to Process One Invoice After Automation (minutes)', min_value=0.0, value=1.5)
    
    # Automation rate
    automation_rate = st.number_input('Automation Rate (%)', min_value=0, max_value=100, value=70)

    automation_system_cost = st.number_input('AP Automation System Cost ($ per year)', min_value=0.0, value=120000.0)
    years = st.number_input('Number of Years for Projection', min_value=1, value=3)

    submit_button = st.form_submit_button(label="Calculate ROI")

if submit_button:
    # Function to calculate progressive time savings over years
    def calculate_time_per_invoice_over_years(initial_time_per_invoice, automation_rate, years):
        time_per_invoice_years = []
        automation_rates = []
        
        # Loop through the years to simulate progressive automation
        for year in range(0, years + 1):
            # Calculate the automation rate for the current year (using exponential progression)
            if year == 0:
                current_automation_rate = 0  # Start with no automation in Year 0
            else:
                current_automation_rate = 1 - (1 - automation_rate / 100) ** (year / years)
            
            # Ensure we are calculating valid numbers for time per invoice
            time_per_invoice = initial_time_per_invoice * (1 - current_automation_rate)
            
            # Append the time per invoice for the current year to the list
            time_per_invoice_years.append(time_per_invoice)
            
            # Store the automation rate for the current year (as a percentage)
            automation_rates.append(current_automation_rate * 100)
    
        # Return both the time per invoice and automation rates over the years
        return time_per_invoice_years, automation_rates
    
    # Call the function
    time_per_invoice_years, automation_rates = calculate_time_per_invoice_over_years(initial_time_per_invoice, automation_rate, years)
    
    # Function to calculate ROI, time saved, processors saved, and net savings
    def calculate_roi_with_growth(current_invoice_volume, growth_rate, years, ap_processor_salary, num_ap_processors, 
                                  missed_discounts, initial_time_per_invoice, time_per_invoice_after, 
                                  automation_system_cost, automation_rate):
        
        # Call the function to get time savings per year
        time_per_invoice_years, automation_rates = calculate_time_per_invoice_over_years(initial_time_per_invoice, automation_rate, years)
    
        # Ensure that the annual invoice volume is calculated correctly
        growth_multiplier = (1 + growth_rate / 100) ** years
        annual_invoice_volume = current_invoice_volume * 12 * growth_multiplier
    
        # Calculate the total time spent processing invoices each year with progressive automation
        total_time_saved_years = []
        for year, time_per_invoice in enumerate(time_per_invoice_years):
            total_time_per_year = annual_invoice_volume * time_per_invoice / 60  # Convert to hours
            total_time_saved_years.append(total_time_per_year)
    
        # Total time saved is the difference between year 0 (no automation) and year N (full automation)
        total_time_saved_hours = total_time_saved_years[0] - total_time_saved_years[-1]   

        # Total time saved for non-automated invoices
        non_automated_invoice_volume = annual_invoice_volume * (1 - automation_rate / 100)
        total_time_saved_non_automated = non_automated_invoice_volume * (initial_time_per_invoice / 60 - time_per_invoice_after / 60)

        # Calculate total hours saved correctly
        total_hours_saved = total_time_saved_non_automated 
                                      
        # Ensure valid processors saved calculation
        working_hours_per_year = 2080
        processors_saved = total_hours_saved / working_hours_per_year
    
        # Ensure processors saved does not exceed the number of AP processors
        processors_saved = min(processors_saved, num_ap_processors)
    
        # Calculate labor cost savings based on time saved
        if processors_saved < 1:
            total_labor_cost_savings = processors_saved / ap_processor_salary
        else:
            total_labor_cost_savings = processors_saved * ap_processor_salary
            
        # Early payer discount savings (realistic cap based on annual)
        early_payer_discount_savings = missed_discounts
    
        # Total savings (labor cost + early payer discounts)
        total_savings = total_labor_cost_savings + early_payer_discount_savings

        # Investment in AP automation system
        total_investment = automation_system_cost * years
                                      
        # Cumulative savings and investment over the years
        cumulative_savings = [total_savings * (year + 1) for year in range(years)]
        cumulative_investment = [automation_system_cost * (year + 1) for year in range(years)]
        net_savings = [cumulative_savings[year] - cumulative_investment[year] for year in range(years)]
        roi_over_time = [(cumulative_savings[year] / cumulative_investment[year]) * 100 for year in range(years)]
    
        # Processor Productivity Gains
        non_automated_invoice_volume = annual_invoice_volume * (1 - automation_rate / 100)

        # Calculate invoices per processor after automation
        if processors_saved < num_ap_processors:
            remaining_processors = num_ap_processors - processors_saved
            invoices_per_processor_after = non_automated_invoice_volume / remaining_processors
        else:
            # If all processors are saved, then there's no manual work left
            invoices_per_processor_after = 0

        # Return results
        return {
            "Projected Invoice Volume": annual_invoice_volume,
            "Labor Cost Savings ($)": total_labor_cost_savings,
            "Early Payer Discount Savings ($)": early_payer_discount_savings,
            "Total Savings ($)": total_savings,
            "Net Savings": net_savings,
            "Processors Saved": processors_saved,
            "Time Efficiency Gain": total_time_saved_hours,
            "Processor Productivity Gains": invoices_per_processor_after,
            "ROI (%)": roi_over_time[-1],
            "ROI Over Time": roi_over_time,
            "Hours Saved": total_hours_saved,
            "Cumulative Savings": cumulative_savings,
            "Cumulative Investment": cumulative_investment,
            "Time Per Invoice Over Years": time_per_invoice_years,
            "Automation Rate Over Years": automation_rates
        }

    # Calculate ROI with growth projection
    results = calculate_roi_with_growth(current_invoice_volume, growth_rate, years, ap_processor_salary, num_ap_processors, 
                                  missed_discounts, initial_time_per_invoice, time_per_invoice_after, 
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
        legend=dict(title_font=dict(color=WHITE), font=dict(color=WHITE))
    )
    st.plotly_chart(roi_fig, use_container_width=True)

    # Ensure the function returns valid data
    if time_per_invoice_years:
        # Create the chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(0, years + 1)), y=time_per_invoice_years,
                                 mode='lines+markers', name='Time Per Invoice (Minutes)'))
    
        # Update the layout of the plot
        fig.update_layout(
            title='Time to Process Invoice Over 3 Years with Automation',
            xaxis_title='Years',
            yaxis_title='Time Per Invoice (Minutes)',
            plot_bgcolor='white'
        )
    
        # Show the chart in Streamlit
        st.plotly_chart(fig)
    else:
        st.write("Error: No data generated for time per invoice.")

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
        legend=dict(title_font=dict(color=WHITE), font=dict(color=WHITE))
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
