-- PayTR Orders Table Schema
-- This table stores payment orders and their status from PayTR

-- Create the orders table
CREATE TABLE orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    merchant_oid TEXT UNIQUE NOT NULL, -- PayTR's unique order identifier
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Payment details
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed')),
    amount_kurus INTEGER NOT NULL, -- Amount in kuruş (e.g., 999 for 9.99 TL)
    currency TEXT NOT NULL DEFAULT 'TL',
    
    -- PayTR basket and details
    basket_json JSONB NOT NULL, -- Base64 decoded basket from PayTR
    user_basket_base64 TEXT NOT NULL, -- Original base64 basket sent to PayTR
    
    -- Customer information (from PayTR)
    customer_email TEXT,
    customer_name TEXT,
    customer_address TEXT,
    customer_phone TEXT,
    
    -- PayTR response fields
    total_amount_kurus INTEGER, -- Final amount after installments (if any)
    failed_reason_code TEXT,
    failed_reason_msg TEXT,
    
    -- PayTR configuration used
    test_mode BOOLEAN DEFAULT true,
    no_installment INTEGER DEFAULT 0,
    max_installment INTEGER DEFAULT 0,
    timeout_limit INTEGER DEFAULT 30,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_orders_merchant_oid ON orders(merchant_oid);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Enable Row Level Security
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own orders
CREATE POLICY "Users can view their own orders" ON orders
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create their own orders
CREATE POLICY "Users can create their own orders" ON orders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own orders (for status updates from PayTR callback)
CREATE POLICY "Users can update their own orders" ON orders
    FOR UPDATE USING (auth.uid() = user_id);

-- Service role can access all orders (for backend operations)
CREATE POLICY "Service role can access all orders" ON orders
    FOR ALL USING (auth.role() = 'service_role');

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Create an order_events table for audit trail
CREATE TABLE order_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- 'created', 'payment_success', 'payment_failed', 'callback_received'
    event_data JSONB, -- Additional event-specific data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on order_events
ALTER TABLE order_events ENABLE ROW LEVEL SECURITY;

-- RLS policies for order_events
CREATE POLICY "Users can view their own order events" ON order_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM orders 
            WHERE orders.id = order_events.order_id 
            AND orders.user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can access all order events" ON order_events
    FOR ALL USING (auth.role() = 'service_role');

-- Create indexes for order_events
CREATE INDEX idx_order_events_order_id ON order_events(order_id);
CREATE INDEX idx_order_events_event_type ON order_events(event_type);
CREATE INDEX idx_order_events_created_at ON order_events(created_at);

-- Optional: Create a view for order summary
CREATE VIEW order_summary AS
SELECT 
    o.id,
    o.merchant_oid,
    o.user_id,
    o.status,
    o.amount_kurus,
    o.currency,
    o.customer_email,
    o.customer_name,
    o.total_amount_kurus,
    o.failed_reason_code,
    o.failed_reason_msg,
    o.test_mode,
    o.created_at,
    o.updated_at,
    -- Calculate amount in TL
    ROUND(o.amount_kurus / 100.0, 2) as amount_tl,
    ROUND(COALESCE(o.total_amount_kurus, o.amount_kurus) / 100.0, 2) as total_amount_tl
FROM orders o;

-- Grant permissions to authenticated users
GRANT SELECT ON order_summary TO authenticated;
GRANT SELECT ON order_events TO authenticated;

-- Grant all permissions to service role
GRANT ALL ON orders TO service_role;
GRANT ALL ON order_events TO service_role;
GRANT ALL ON order_summary TO service_role;
