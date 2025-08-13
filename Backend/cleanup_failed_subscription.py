#!/usr/bin/env python3
"""
Cleanup script for failed subscriptions
This script helps clean up subscriptions that were created but never had a successful payment.
"""

import os
import sys
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("ERROR: Missing Supabase configuration")
    print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables")
    sys.exit(1)

def get_supabase_client() -> Client:
    """Get Supabase client with service role key"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def cleanup_failed_subscriptions(user_id: str = None):
    """Clean up failed subscriptions"""
    supabase = get_supabase_client()
    
    print("🔍 Looking for failed subscriptions...")
    
    # Find subscriptions that are active but have no successful payments
    query = (
        supabase
        .table('subscriptions')
        .select('*')
        .eq('status', 'active')
        .is_('last_payment_order_id', 'null')
    )
    
    if user_id:
        query = query.eq('user_id', user_id)
        print(f"🔍 Looking for user: {user_id}")
    
    result = query.execute()
    
    if not result.data:
        print("✅ No failed subscriptions found")
        return []
    
    print(f"📋 Found {len(result.data)} potentially failed subscriptions")
    
    failed_subscriptions = result.data
    cleaned_subscriptions = []
    
    for subscription in failed_subscriptions:
        print(f"\n📝 Checking subscription: {subscription['id']}")
        print(f"   User: {subscription['user_id']}")
        print(f"   Plan: {subscription['plan_id']}")
        print(f"   Status: {subscription['status']}")
        print(f"   Created: {subscription['created_at']}")
        
        # Check if there are any paid billing periods
        billing_result = (
            supabase
            .table('subscription_billing_periods')
            .select('*')
            .eq('subscription_id', subscription['id'])
            .eq('status', 'paid')
            .execute()
        )
        
        if billing_result.data:
            print(f"   ✅ Has paid billing periods - keeping subscription")
            continue
        
        # Check if there are any pending billing periods
        pending_billing_result = (
            supabase
            .table('subscription_billing_periods')
            .select('*')
            .eq('subscription_id', subscription['id'])
            .eq('status', 'pending')
            .execute()
        )
        
        if pending_billing_result.data:
            print(f"   ⚠️  Has pending billing periods - checking orders...")
            
            # Check if there are any orders for this subscription
            orders_result = (
                supabase
                .table('orders')
                .select('*')
                .eq('user_id', subscription['user_id'])
                .execute()
            )
            
            if orders_result.data:
                print(f"   📦 Found {len(orders_result.data)} orders for user")
                for order in orders_result.data:
                    print(f"      Order: {order['merchant_oid']} - Status: {order['status']}")
                    if order['status'] == 'paid':
                        print(f"      ✅ Found paid order - keeping subscription")
                        break
                else:
                    print(f"      ❌ No paid orders found - marking as failed")
            else:
                print(f"   ❌ No orders found - marking as failed")
        else:
            print(f"   ❌ No billing periods found - marking as failed")
        
        # Mark subscription as failed
        update_result = (
            supabase
            .table('subscriptions')
            .update({
                'status': 'failed',
                'updated_at': datetime.now().isoformat()
            })
            .eq('id', subscription['id'])
            .execute()
        )
        
        if update_result.data:
            cleaned_subscriptions.append(update_result.data[0])
            print(f"   ✅ Marked as failed")
            
            # Create cleanup event
            try:
                supabase.table('subscription_events').insert({
                    'subscription_id': subscription['id'],
                    'event_type': 'cleanup_failed',
                    'event_data': {
                        'reason': 'No successful payment found',
                        'cleaned_at': datetime.now().isoformat()
                    }
                }).execute()
                print(f"   📝 Created cleanup event")
            except Exception as e:
                print(f"   ⚠️  Failed to create cleanup event: {e}")
        else:
            print(f"   ❌ Failed to update subscription")
    
    print(f"\n🎉 Cleanup complete! Marked {len(cleaned_subscriptions)} subscriptions as failed")
    return cleaned_subscriptions

def list_all_subscriptions():
    """List all subscriptions for debugging"""
    supabase = get_supabase_client()
    
    print("📋 All subscriptions in database:")
    
    result = supabase.table('subscriptions').select('*').execute()
    
    if not result.data:
        print("No subscriptions found")
        return
    
    for subscription in result.data:
        print(f"\n📝 Subscription: {subscription['id']}")
        print(f"   User: {subscription['user_id']}")
        print(f"   Plan: {subscription['plan_id']}")
        print(f"   Status: {subscription['status']}")
        print(f"   Created: {subscription['created_at']}")
        print(f"   Last Payment Order: {subscription.get('last_payment_order_id', 'None')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_all_subscriptions()
        elif command == "cleanup":
            user_id = sys.argv[2] if len(sys.argv) > 2 else None
            cleanup_failed_subscriptions(user_id)
        else:
            print("Usage:")
            print("  python cleanup_failed_subscription.py list")
            print("  python cleanup_failed_subscription.py cleanup [user_id]")
    else:
        print("Usage:")
        print("  python cleanup_failed_subscription.py list")
        print("  python cleanup_failed_subscription.py cleanup [user_id]")
        print("\nExamples:")
        print("  python cleanup_failed_subscription.py list")
        print("  python cleanup_failed_subscription.py cleanup")
        print("  python cleanup_failed_subscription.py cleanup 123e4567-e89b-12d3-a456-426614174000")
