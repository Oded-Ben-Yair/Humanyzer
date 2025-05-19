"""
Subscription management page for Humanyze.
"""
import streamlit as st
import requests
import json
from datetime import datetime
from ui.auth import auth_required, get_auth_header
from ui.ui_utils import get_api_url

# API endpoints
API_URL = get_api_url()
SUBSCRIPTION_ENDPOINT = f"{API_URL}/api/payments/subscription"
PLANS_ENDPOINT = f"{API_URL}/api/payments/plans"
CHECKOUT_ENDPOINT = f"{API_URL}/api/payments/create-checkout-session"
PORTAL_ENDPOINT = f"{API_URL}/api/payments/create-customer-portal"
LIMIT_ENDPOINT = f"{API_URL}/api/payments/subscription/check-limit"


def format_currency(amount, currency="USD"):
    """Format amount as currency."""
    if currency.upper() == "USD":
        return f"${amount/100:.2f}"
    return f"{amount/100:.2f} {currency.upper()}"


def format_date(date_str):
    """Format date string."""
    if not date_str:
        return "N/A"
    
    try:
        if isinstance(date_str, str):
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            date = date_str
        return date.strftime("%B %d, %Y")
    except Exception:
        return date_str


@auth_required
def show_subscription_page():
    """Display subscription management page."""
    st.title("Subscription Management")
    
    # Get auth header
    auth_header = get_auth_header()
    if not auth_header:
        st.error("Authentication error. Please log in again.")
        return
    
    # Fetch current subscription
    try:
        response = requests.get(
            SUBSCRIPTION_ENDPOINT,
            headers=auth_header
        )
        
        if response.status_code == 200:
            subscription = response.json()
        else:
            st.error(f"Error fetching subscription: {response.text}")
            return
    except Exception as e:
        st.error(f"Error fetching subscription: {str(e)}")
        return
    
    # Fetch available plans
    try:
        response = requests.get(PLANS_ENDPOINT)
        
        if response.status_code == 200:
            plans_data = response.json()
            plans = plans_data.get("plans", [])
        else:
            st.error(f"Error fetching plans: {response.text}")
            return
    except Exception as e:
        st.error(f"Error fetching plans: {str(e)}")
        return
    
    # Fetch usage limits
    try:
        response = requests.get(
            LIMIT_ENDPOINT,
            headers=auth_header
        )
        
        if response.status_code == 200:
            usage = response.json()
        else:
            usage = None
    except Exception:
        usage = None
    
    # Display current subscription
    st.header("Current Subscription")
    
    current_tier = subscription.get("tier", "free")
    status = subscription.get("status", "active")
    
    # Find current plan details
    current_plan = next((p for p in plans if p["tier"] == current_tier), None)
    
    if current_plan:
        st.subheader(f"{current_plan['name']} Plan")
        
        # Status indicator
        status_color = {
            "active": "green",
            "trialing": "blue",
            "past_due": "orange",
            "canceled": "red",
            "incomplete": "orange",
            "incomplete_expired": "red",
            "unpaid": "red"
        }.get(status, "gray")
        
        st.markdown(
            f"<div style='display: flex; align-items: center; margin-bottom: 20px;'>"
            f"<div style='background-color: {status_color}; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px;'></div>"
            f"<div>Status: <strong>{status.title()}</strong></div>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Subscription period
        if subscription.get("current_period_start") and subscription.get("current_period_end"):
            st.markdown(
                f"**Current Period:** {format_date(subscription['current_period_start'])} to "
                f"{format_date(subscription['current_period_end'])}"
            )
        
        # Cancel at period end
        if subscription.get("cancel_at_period_end"):
            st.warning("Your subscription will be canceled at the end of the current billing period.")
        
        # Display usage if available
        if usage:
            st.subheader("Usage")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if "character_limit" in usage and "characters_used" in usage:
                    progress = min(100, (usage["characters_used"] / usage["character_limit"]) * 100)
                    st.markdown(f"**Characters Used:** {usage['characters_used']:,} / {usage['character_limit']:,}")
                    st.progress(progress / 100)
            
            with col2:
                if "request_limit" in usage and "requests_used" in usage:
                    progress = min(100, (usage["requests_used"] / usage["request_limit"]) * 100)
                    st.markdown(f"**Requests Used:** {usage['requests_used']} / {usage['request_limit']}")
                    st.progress(progress / 100)
        
        # Features
        st.subheader("Features")
        features = subscription.get("features", {})
        
        feature_icons = {
            "custom_profiles": "✅" if features.get("custom_profiles") else "❌",
            "priority_processing": "✅" if features.get("priority_processing") else "❌",
            "advanced_analytics": "✅" if features.get("advanced_analytics") else "❌",
            "api_access": "✅" if features.get("api_access") else "❌",
            "dedicated_support": "✅" if features.get("dedicated_support") else "❌"
        }
        
        st.markdown(f"**Custom Profiles:** {feature_icons['custom_profiles']}")
        st.markdown(f"**Priority Processing:** {feature_icons['priority_processing']}")
        st.markdown(f"**Advanced Analytics:** {feature_icons['advanced_analytics']}")
        st.markdown(f"**API Access:** {feature_icons['api_access']}")
        st.markdown(f"**Dedicated Support:** {feature_icons['dedicated_support']}")
        
        # Manage subscription button
        if current_tier != "free" and status in ["active", "trialing", "past_due"]:
            if st.button("Manage Subscription", type="primary"):
                try:
                    response = requests.post(
                        PORTAL_ENDPOINT,
                        headers=auth_header,
                        json={"return_url": f"{st.query_params.get('base_url', '')}/subscription"}
                    )
                    
                    if response.status_code == 200:
                        portal_data = response.json()
                        portal_url = portal_data.get("url")
                        
                        if portal_url:
                            st.markdown(f"[Click here to manage your subscription]({portal_url})")
                        else:
                            st.error("Error creating customer portal session.")
                    else:
                        st.error(f"Error creating customer portal session: {response.text}")
                except Exception as e:
                    st.error(f"Error creating customer portal session: {str(e)}")
    else:
        st.info("You are currently on the Free plan.")
    
    # Available plans
    st.header("Available Plans")
    
    # Create columns for plans
    plan_cols = st.columns(len(plans))
    
    for i, plan in enumerate(plans):
        with plan_cols[i]:
            # Highlight current plan
            is_current = plan["tier"] == current_tier
            
            # Plan card
            card_style = "border: 2px solid #4CAF50; padding: 20px; border-radius: 10px;" if is_current else "border: 1px solid #ddd; padding: 20px; border-radius: 10px;"
            
            st.markdown(
                f"<div style='{card_style}'>"
                f"<h3 style='text-align: center;'>{plan['name']}</h3>"
                f"<p style='text-align: center; font-size: 24px; font-weight: bold;'>{format_currency(plan['price_amount'])}<span style='font-size: 14px; font-weight: normal;'>/{plan['interval']}</span></p>"
                f"<p style='text-align: center;'>{plan['description']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
            
            # Feature list
            features = plan.get("features", {})
            
            st.markdown(f"✓ {features.get('max_characters_per_month', 0):,} characters/month")
            st.markdown(f"✓ {features.get('max_requests_per_day', 0)} requests/day")
            
            if features.get("custom_profiles"):
                st.markdown("✓ Custom profiles")
            
            if features.get("priority_processing"):
                st.markdown("✓ Priority processing")
            
            if features.get("advanced_analytics"):
                st.markdown("✓ Advanced analytics")
            
            if features.get("api_access"):
                st.markdown("✓ API access")
            
            if features.get("dedicated_support"):
                st.markdown("✓ Dedicated support")
            
            # Subscribe button
            if not is_current and plan["tier"] != "free":
                if st.button(f"Subscribe to {plan['name']}", key=f"subscribe_{plan['id']}"):
                    try:
                        # Create checkout session
                        response = requests.post(
                            CHECKOUT_ENDPOINT,
                            headers=auth_header,
                            json={
                                "price_id": plan["price_id"],
                                "success_url": f"{st.query_params.get('base_url', '')}/subscription?success=true",
                                "cancel_url": f"{st.query_params.get('base_url', '')}/subscription?canceled=true"
                            }
                        )
                        
                        if response.status_code == 200:
                            checkout_data = response.json()
                            checkout_url = checkout_data.get("url")
                            
                            if checkout_url:
                                st.markdown(f"[Click here to complete your subscription]({checkout_url})")
                            else:
                                st.error("Error creating checkout session.")
                        else:
                            st.error(f"Error creating checkout session: {response.text}")
                    except Exception as e:
                        st.error(f"Error creating checkout session: {str(e)}")
            elif is_current:
                st.info("Current Plan")


# Run the app
if __name__ == "__main__":
    show_subscription_page()
