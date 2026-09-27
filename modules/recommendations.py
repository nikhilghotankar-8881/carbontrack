RECOMMENDATIONS = {
    "Electricity": "💡 **Electricity is your largest footprint contributor.** Consider switching to LED lighting, unplugging standby electronics, and using energy-efficient inverter appliances.",
    "Fuel": "⛽ **Fuel consumption is your highest emission category.** Try combining multiple errands into a single trip, avoiding aggressive acceleration, or using fuel-efficient driving habits.",
    "Transport": "🚗 **Transportation emissions are leading your footprint.** Opt for public transit, metro, train, or carpooling whenever available to significantly reduce travel emissions.",
    "Food": "🍎 **Food & grocery spending is your top emission source.** Minimizing food waste, buying locally produced items, and incorporating plant-rich meals can lower your food footprint.",
    "Clothing": "👕 **Clothing & apparel purchases represent your highest footprint.** Extending garment lifespans through repairs, buying durable quality clothes, or opting for thrift/second-hand items lowers fast-fashion impact.",
    "Electronics": "📱 **Electronics purchases are your highest contributor.** Extend device usage cycles, repair appliances before replacing, and recycle e-waste responsibly.",
    "Household": "🏠 **Household goods are your primary footprint source.** Choose eco-labeled household goods, bulk buy cleaning supplies, and eliminate single-use plastic products.",
    "Other": "📦 **General consumer spend is your largest contributor.** Review your miscellaneous purchases to identify opportunities for mindful, low-carbon alternatives."
}

def get_recommendation_for_category(category: str) -> str:
    """Returns rule-based carbon reduction recommendation for the given category."""
    return RECOMMENDATIONS.get(
        category, 
        "🌱 Track your daily purchases and energy usage to identify specific carbon reduction opportunities."
    )
