import streamlit as st
import matplotlib.pyplot as plt

# Cities dictionary with latitudes
cities = {
    "London, UK": 51.5,
    "Edinburgh, UK": 55.95,
    "Cardiff, UK": 51.48,
    "Belfast, UK": 54.6,
    "Manchester, UK": 53.48,
    "Birmingham, UK": 52.48,
    "Glasgow, UK": 55.86,
    "Liverpool, UK": 53.41,
    "Bristol, UK": 51.45,
    "Sheffield, UK": 53.38,
    "New York, USA": 40.71,
    "Sydney, Australia": -33.87,
    "Tokyo, Japan": 35.68,
    "Cape Town, South Africa": -33.92,
    "Rio de Janeiro, Brazil": -22.91,
    "Mumbai, India": 19.08,
    "Beijing, China": 39.90,
    "Moscow, Russia": 55.75,
    "Dubai, UAE": 25.20,
    "Toronto, Canada": 43.65,
}

# Estimate peak sun hours based on latitude
def estimate_peak_sun_hours(latitude):
    """Estimate average peak sun hours per day based on latitude."""
    lat = abs(latitude)
    if lat > 90:
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    psh = 6 - (4 * lat / 90)
    return max(psh, 2)

# Calculate solar farm metrics
def calculate_solar_farm_metrics(latitude, land_size_m2, electricity_price_gbp_per_kwh, upfront_costs_per_m2, annual_running_costs):
    """Calculate energy yield, revenue, costs, and additional metrics in GBP."""
    panel_area_per_kw = 10  # m² per kW
    carbon_offset_kg_per_kwh = 0.5  # kg CO2 per kWh
    avg_home_consumption_kwh = 3500  # kWh per year
    co2_per_car_tonnes = 4.6  # tonnes CO2 per car per year

    # System size in kW
    system_size_kw = land_size_m2 / panel_area_per_kw

    # Peak sun hours
    psh = estimate_peak_sun_hours(latitude)

    # Annual energy yield
    daily_energy_kwh = system_size_kw * psh
    annual_energy_kwh = daily_energy_kwh * 365

    # Annual revenue in GBP
    annual_revenue_gbp = annual_energy_kwh * electricity_price_gbp_per_kwh

    # Total upfront costs in GBP
    total_upfront_costs_gbp = upfront_costs_per_m2 * land_size_m2

    # Net annual profit in GBP
    net_annual_profit_gbp = annual_revenue_gbp - annual_running_costs

    # Break-even time
    break_even_years = total_upfront_costs_gbp / net_annual_profit_gbp if net_annual_profit_gbp > 0 else float('inf')

    # Carbon offset in tonnes
    annual_carbon_offset_tonnes = (annual_energy_kwh * carbon_offset_kg_per_kwh) / 1000

    # Land size comparison to football pitches
    football_pitch_m2 = 7140
    pitches_equivalent = land_size_m2 / football_pitch_m2

    # Homes powered
    number_of_homes = annual_energy_kwh / avg_home_consumption_kwh

    # Equivalent cars off the road
    equivalent_cars = annual_carbon_offset_tonnes / co2_per_car_tonnes

    return annual_energy_kwh, annual_revenue_gbp, total_upfront_costs_gbp, annual_running_costs, net_annual_profit_gbp, break_even_years, annual_carbon_offset_tonnes, pitches_equivalent, number_of_homes, equivalent_cars

# Streamlit app
def main():
    st.set_page_config(page_title="Solar Farm Estimator", page_icon="🌞")

    # Sidebar inputs
    st.sidebar.title("Input Parameters")
    location_method = st.sidebar.radio("Location", ["Select city", "Enter latitude"])
    if location_method == "Select city":
        city = st.sidebar.selectbox("City", sorted(cities.keys()))
        latitude = cities[city]
    else:
        latitude = st.sidebar.number_input("Latitude (-90 to 90)", min_value=-90.0, max_value=90.0, value=51.5)

    land_size_m2 = st.sidebar.slider("Land Size (m²)", min_value=100.0, max_value=1000000.0, value=10000.0, step=1000.0)
    electricity_price_gbp_per_kwh = st.sidebar.slider("Electricity Price (GBP/kWh)", min_value=0.05, max_value=0.20, value=0.10, step=0.01)
    upfront_costs_per_m2 = st.sidebar.slider("Upfront Costs per m² (GBP)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
    
    # Dynamic default for running costs
    default_running_costs = 15 * (land_size_m2 / 10)  # 15 GBP/kW/year
    annual_running_costs = st.sidebar.slider("Annual Running Costs (GBP/year)", min_value=0.0, max_value=1000000.0, value=default_running_costs, step=1000.0)

    # Main content
    st.title("Solar Farm Estimator")
    st.write("Estimate the potential of your solar farm by adjusting the parameters.")

    if st.button("Calculate"):
        try:
            metrics = calculate_solar_farm_metrics(latitude, land_size_m2, electricity_price_gbp_per_kwh, upfront_costs_per_m2, annual_running_costs)
            annual_energy_kwh, annual_revenue_gbp, total_upfront_costs_gbp, annual_running_costs, net_annual_profit_gbp, break_even_years, annual_carbon_offset_tonnes, pitches_equivalent, number_of_homes, equivalent_cars = metrics

            # Suggested running costs note
            suggested_running_costs = 15 * (land_size_m2 / 10)
            st.write(f"**Note:** For your land size of {land_size_m2:,} m², suggested annual running costs are £{suggested_running_costs:,.2f} (based on 15 GBP/kW/year, 10 m²/kW).")

            # Results
            st.subheader("📊 Results")
            st.metric("Annual Energy Yield", f"{annual_energy_kwh:,.0f} kWh")
            st.metric("Annual Revenue", f"£{annual_revenue_gbp:,.2f}")
            st.metric("Total Upfront Costs", f"£{total_upfront_costs_gbp:,.2f}")
            st.metric("Annual Running Costs", f"£{annual_running_costs:,.2f}")
            st.metric("Net Annual Profit", f"£{net_annual_profit_gbp:,.2f}")
            st.metric("Break-Even Time", f"{break_even_years:.2f} years" if break_even_years != float('inf') else "Never")
            st.metric("Carbon Offset", f"{annual_carbon_offset_tonnes:.2f} tonnes/year")
            st.write(f"**Land Size Equivalent:** ~{pitches_equivalent:.2f} football pitches")

            # Cool features
            st.write(f"**Homes Powered:** Approximately {number_of_homes:.0f} homes")
            st.write(f"**Environmental Impact:** Equivalent to ~{equivalent_cars:.0f} cars off the road/year")

            # Cost breakdown pie chart
            total_running_costs_10_years = 10 * annual_running_costs
            labels = ['Upfront Costs', 'Running Costs (10 years)']
            sizes = [total_upfront_costs_gbp, total_running_costs_10_years]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.subheader("Cost Breakdown Over 10 Years")
            st.pyplot(fig)

            st.write("""
            **Notes:**
            - Assumes 10 m² per kW.
            - Carbon offset: 0.5 kg CO2/kWh.
            - Home consumption: 3,500 kWh/year.
            - Car CO2: 4.6 tonnes/year.
            - Results are estimates; actual values may vary.
            """)

        except ValueError as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()


st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write("Solar Farm Estimator © ¦ Created by Tom Loosley ¦ Published in 2025")
st.markdown("Found a problem? <a href='mailto:loosleytom@gmail.com'>Report an issue</a>", unsafe_allow_html=True)
