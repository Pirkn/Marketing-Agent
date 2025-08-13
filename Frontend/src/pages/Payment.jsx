import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { paymentService } from '../services/paymentService';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Loader2, CreditCard, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

function Payment() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showIframe, setShowIframe] = useState(false);
  const [token, setToken] = useState('');
  const [merchantOid, setMerchantOid] = useState('');
  const [formData, setFormData] = useState({
    customer: {
      email: user?.email || '',
      name: '',
      address: '',
      phone: ''
    }
  });

  // Load PayTR iFrame script
  useEffect(() => {
    if (showIframe && token) {
      const script = document.createElement('script');
      script.src = 'https://www.paytr.com/js/iframeResizer.min.js';
      script.onload = () => {
        // Initialize iFrame resizer after script loads
        if (window.iFrameResize) {
          window.iFrameResize({}, '#paytriframe');
        }
      };
      document.head.appendChild(script);

      return () => {
        // Cleanup script when component unmounts
        const existingScript = document.querySelector('script[src="https://www.paytr.com/js/iframeResizer.min.js"]');
        if (existingScript) {
          existingScript.remove();
        }
      };
    }
  }, [showIframe, token]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      customer: {
        ...prev.customer,
        [field]: value
      }
    }));
  };

  const handleStartPayment = async () => {
    if (!formData.customer.email || !formData.customer.name) {
      toast.error('Please fill in email and name');
      return;
    }

    setIsLoading(true);
    try {
      const paymentData = {
        items: [
          {
            name: 'Pro Plan - Marketing Agent',
            price: '9.99',
            quantity: 1
          }
        ],
        customer: formData.customer,
        no_installment: 0,
        max_installment: 0,
        currency: 'TL'
      };

      const result = await paymentService.createPaytrSession(paymentData);
      
      setToken(result.token);
      setMerchantOid(result.merchant_oid);
      setShowIframe(true);
      
      // Store merchant_oid for redirect pages
      localStorage.setItem('last_merchant_oid', result.merchant_oid);
      
      toast.success('Payment session created successfully');
    } catch (error) {
      console.error('Payment error:', error);
      toast.error(error.message || 'Failed to create payment session');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              Authentication Required
            </CardTitle>
            <CardDescription>
              Please sign in to access the payment page.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate('/signin')} className="w-full">
              Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <Button 
            variant="outline" 
            onClick={handleBackToDashboard}
            className="mb-4"
          >
            ← Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">Payment</h1>
          <p className="text-gray-600 mt-2">Complete your purchase to unlock premium features</p>
        </div>

        {!showIframe ? (
          <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Pro Plan - Marketing Agent
              </CardTitle>
              <CardDescription>
                Get access to advanced marketing tools and AI-powered content generation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">What's included:</h3>
                <ul className="text-blue-800 space-y-1 text-sm">
                  <li>• Unlimited AI content generation</li>
                  <li>• Advanced lead generation tools</li>
                  <li>• Priority support</li>
                  <li>• Analytics dashboard</li>
                </ul>
              </div>

              <div className="text-center py-4 border-t border-b">
                <div className="text-3xl font-bold text-gray-900">₺9.99</div>
                <div className="text-gray-600">One-time payment</div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <Input
                    type="email"
                    value={formData.customer.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    placeholder="your@email.com"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <Input
                    type="text"
                    value={formData.customer.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="John Doe"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address
                  </label>
                  <Textarea
                    value={formData.customer.address}
                    onChange={(e) => handleInputChange('address', e.target.value)}
                    placeholder="Your address"
                    rows={2}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <Input
                    type="tel"
                    value={formData.customer.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    placeholder="5551234567"
                  />
                </div>
              </div>

              <Button 
                onClick={handleStartPayment} 
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Payment Session...
                  </>
                ) : (
                  <>
                    <CreditCard className="mr-2 h-4 w-4" />
                    Proceed to Payment
                  </>
                )}
              </Button>

              <p className="text-xs text-gray-500 text-center">
                Your payment is processed securely by PayTR. We never store your payment information.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="w-full max-w-4xl mx-auto">
            <Card>
              <CardHeader>
                <CardTitle>Complete Your Payment</CardTitle>
                <CardDescription>
                  Please complete your payment using the secure form below
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="w-full h-96">
                  <iframe
                    src={`https://www.paytr.com/odeme/guvenli/${token}`}
                    id="paytriframe"
                    frameBorder="0"
                    scrolling="no"
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
                <div className="mt-4 text-center text-sm text-gray-600">
                  <p>Order ID: {merchantOid}</p>
                  <p>You will be redirected after payment completion</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

export default Payment;
