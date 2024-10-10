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

# Input fields
current_invoice_volume = st.number_input('Current Invoice Volume per Month', min_value=0, value=5000)
growth_rate = st.number_input('Projected Growth Rate (%)', min_value=0, max_value=100, value=10)
ap_processor_salary = st.number_input('AP Processor Salary ($)', min_value=0.00, value=50000.00)
num_ap_processors = st.number_input('Number of AP Processors', min_value=1, value=3)
missed_discounts = st.number_input('Missed Early Payer Discounts ($ per year)', min_value=0.00, value=20000.00)
ap_implementation_fee = st.number_input('Implementation Fee', min_value=0.00, value=25000.00)
payments_implementation_fee = st.number_input('Payments Implementation Fee', min_value=0.00, value=15000.00)
# AP Automation System Cost
automation_system_cost = st.number_input('Annual Recurring Cost', min_value=0.0, value=20000.0)

# Time to process invoices before/after automation
initial_time_per_invoice = st.number_input('Time to Process One Invoice Before Automation (minutes)', min_value=0.0, value=10.0)
time_per_invoice_after = st.number_input('Time to Process One Invoice After Automation (minutes)', min_value=0.0, value=2.0)

# Automation rate
automation_rate = st.number_input('Automation Rate (%)', min_value=0, max_value=100, value=70)

# Number of years for the projection
years = st.number_input('Number of Years for Projection', min_value=1, value=3)


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

    # Calculate total hours saved from automation
    automated_invoice_volume = annual_invoice_volume * (automation_rate / 100)
                                  
   
                    
    # Total time spent for non-automated invoices
    non_automated_invoice_volume = annual_invoice_volume * (1 - automation_rate / 100)
    total_time_non_automated = non_automated_invoice_volume * (time_per_invoice_after/ 60)

    # Adjust non_automated_invoice_volume and manual processing time
    if time_per_invoice_after > 0:
        remaining_manual_invoices = non_automated_invoice_volume * (initial_time_per_invoice / time_per_invoice_after)
    else:
        remaining_manual_invoices = non_automated_invoice_volume  # To avoid dividing by zero

    
    # Calculate the time saved per invoice (converted to hours)
    time_saved_per_invoice = (initial_time_per_invoice - time_per_invoice_after) / 60
    
    total_hours_saved_from_automation = automated_invoice_volume * time_saved_per_invoice
                                  
    # Calculate the number of processors needed after automation for non-automated invoices
    working_hours_per_year = 2080
    processors_needed_after_automation = total_time_non_automated / working_hours_per_year
    
    # Calculate the number of processors saved based on the remaining manual workload
    processors_saved = num_ap_processors - processors_needed_after_automation
    
    # Ensure processors_saved is a positive number and does not exceed the original number of AP processors
    processors_saved = max(0, min(processors_saved, num_ap_processors))

    # Calculate total hours saved from automation
    total_hours_saved = automated_invoice_volume * time_saved_per_invoice

    # **Calculate labor cost savings based on total hours saved**
    hourly_rate_per_processor = ap_processor_salary / working_hours_per_year
    total_labor_cost_savings = total_hours_saved * hourly_rate_per_processor
        
    # Early payer discount savings (realistic cap based on annual)
    early_payer_discount_savings = missed_discounts

    # Total savings (labor cost + early payer discounts)
    total_savings = total_labor_cost_savings + early_payer_discount_savings

    # Investment in AP automation system (implementation fees only in Year 0)
    total_investment = []
    for year in range(years):
        if year == 0:
            # Year 0 includes implementation fees
            total_investment.append(automation_system_cost + ap_implementation_fee + payments_implementation_fee)
        else:
            # Subsequent years only include the recurring system cost
            total_investment.append(automation_system_cost)

    # Cumulative savings and investment over the years
    cumulative_savings = []
    cumulative_investment = []
    net_savings = []
    roi_over_time = []
    
    # Loop through each year and calculate cumulative values
    for year in range(years):
        # Cumulative savings should reflect the growing savings year by year
        cumulative_saving = total_savings * (year + 1)  # Multiply by (year + 1) to accumulate savings over time
        cumulative_savings.append(cumulative_saving)
        
        # Investment should accumulate year by year as well
        if year == 0:
            cumulative_investment.append(automation_system_cost + ap_implementation_fee + payments_implementation_fee)  # Year 0 includes fees
        else:
            cumulative_investment.append(cumulative_investment[year-1] + automation_system_cost)  # Add only the system cost after Year 0
    
        # Calculate net savings
        net_saving = cumulative_savings[year] - cumulative_investment[year]
        net_savings.append(net_saving)
        
        # Calculate ROI
        if cumulative_investment[year] > 0:  # Avoid division by zero
            roi = (cumulative_savings[year] / cumulative_investment[year]) * 100
        else:
            roi = 0
        roi_over_time.append(roi)

    # Calculate invoices per processor after automation
    remaining_processors = num_ap_processors - processors_saved

    if remaining_processors < 1:
        invoices_per_processor_after = (annual_invoice_volume - automated_invoice_volume) * remaining_processors
    else:
        invoices_per_processor_after = (annual_invoice_volume - automated_invoice_volume) / remaining_processors
                                  
    year_one_costs = automation_system_cost + ap_implementation_fee + payments_implementation_fee
    total_implementation_cost = ap_implementation_fee + payments_implementation_fee
                                  
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
        "Automation Rate Over Years": automation_rates,
        "Year One Costs": year_one_costs,
        "Total Implementation Cost": total_implementation_cost,
        "Annual Recurring Cost": automation_system_cost,
        "Automated Invoice Volume": automated_invoice_volume
    }

# Calculate ROI with growth projection
results = calculate_roi_with_growth(current_invoice_volume, growth_rate, years, ap_processor_salary, num_ap_processors, 
                              missed_discounts, initial_time_per_invoice, time_per_invoice_after, 
                              automation_system_cost, automation_rate)
# Add another horizontal line
st.markdown("---")

#Display Costs
st.markdown("### Costs to Customer")
col1, col2, col3 = st.columns(3)
col1.metric(label="Year 1 Costs", value=f"${int(results['Year One Costs']):,}")
col2.metric(label="Implementation Cost", value=f"${int(results['Total Implementation Cost']):,}")
col3.metric(label="Annual Recurring Cost", value=f"${int(results['Annual Recurring Cost']):,}")

# Add another horizontal line
st.markdown("---")      
            
# Display Efficiency Metrics
st.markdown("### Efficiency Gains")
col1, col2, col3 = st.columns(3)
col1.metric(label="Hours Saved", value=f"{int(results['Hours Saved']):,}")
col2.metric(label="Invoices Requiring Review", value=f"{int(results['Processor Productivity Gains']):.2f}")
col3.metric(label="Automated Invoices", value=f"{int(results['Automated Invoice Volume']):.2f}")


# Add another horizontal line
st.markdown("---")
            
# Display key metrics in a 3x2 grid for clarity
st.markdown("### Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric(label="Projected Invoice Volume", value=f"{int(results['Projected Invoice Volume']):,}")
col1.metric(label="Labor Cost Savings ($)", value=f"${results['Labor Cost Savings ($)']:.2f}")
col2.metric(label="Repurposed Headcount", value=f"{results['Processors Saved']:.2f}")
col2.metric(label="Early Payer Discount Savings ($)", value=f"${results['Early Payer Discount Savings ($)']:.2f}")
col3.metric(label="Total Savings ($)", value=f"${results['Total Savings ($)']:.2f}")
col3.metric(label="ROI (%)", value=f"{results['ROI (%)']:.2f}%")

# Add another horizontal line
st.markdown("---")

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
