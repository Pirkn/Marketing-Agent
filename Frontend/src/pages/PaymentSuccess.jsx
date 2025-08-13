import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { paymentService } from '../services/paymentService';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { CheckCircle, XCircle, Loader2, ArrowRight, Home } from 'lucide-react';
import { toast } from 'sonner';

function PaymentSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [orderStatus, setOrderStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkOrderStatus = async () => {
      try {
        // Get merchant_oid from URL params or localStorage
        const merchantOid = searchParams.get('merchant_oid') || localStorage.getItem('last_merchant_oid');
        
        if (!merchantOid) {
          setError('No order found');
          setIsLoading(false);
          return;
        }

        // Poll for order status
        const status = await paymentService.pollOrderStatus(merchantOid);
        setOrderStatus(status);
        
        // Clear stored merchant_oid
        localStorage.removeItem('last_merchant_oid');
        
        if (status.status === 'paid') {
          toast.success('Payment completed successfully!');
        } else if (status.status === 'failed') {
          toast.error('Payment failed');
        }
      } catch (error) {
        console.error('Error checking order status:', error);
        setError(error.message);
        toast.error('Failed to verify payment status');
      } finally {
        setIsLoading(false);
      }
    };

    checkOrderStatus();
  }, [searchParams]);

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  const handleTryAgain = () => {
    navigate('/payment');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Verifying Payment</h2>
            <p className="text-gray-600 text-center">
              Please wait while we verify your payment status...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <XCircle className="h-12 w-12 text-red-500 mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Verification Error</h2>
            <p className="text-gray-600 text-center mb-6">
              {error}
            </p>
            <div className="space-y-3 w-full">
              <Button onClick={handleGoToDashboard} className="w-full">
                <Home className="mr-2 h-4 w-4" />
                Go to Dashboard
              </Button>
              <Button variant="outline" onClick={handleTryAgain} className="w-full">
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isSuccess = orderStatus?.status === 'paid';
  const isFailed = orderStatus?.status === 'failed';

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardContent className="flex flex-col items-center justify-center py-12">
          {isSuccess ? (
            <>
              <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h2>
              <p className="text-gray-600 text-center mb-6">
                Thank you for your purchase. Your Pro Plan has been activated.
              </p>
              
              {orderStatus.total_amount_kurus && (
                <div className="bg-green-50 p-4 rounded-lg mb-6 w-full">
                  <p className="text-green-800 text-sm">
                    Amount paid: ₺{(orderStatus.total_amount_kurus / 100).toFixed(2)}
                  </p>
                </div>
              )}

              <div className="bg-blue-50 p-4 rounded-lg mb-6 w-full">
                <h3 className="font-semibold text-blue-900 mb-2">What's next?</h3>
                <ul className="text-blue-800 space-y-1 text-sm">
                  <li>• Access all premium features</li>
                  <li>• Generate unlimited content</li>
                  <li>• Use advanced lead generation</li>
                  <li>• Get priority support</li>
                </ul>
              </div>

              <Button onClick={handleGoToDashboard} className="w-full">
                <ArrowRight className="mr-2 h-4 w-4" />
                Go to Dashboard
              </Button>
            </>
          ) : isFailed ? (
            <>
              <XCircle className="h-16 w-16 text-red-500 mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Payment Failed</h2>
              <p className="text-gray-600 text-center mb-6">
                {orderStatus?.failed_reason_msg || 'Your payment could not be processed.'}
              </p>
              
              {orderStatus?.failed_reason_code && (
                <div className="bg-red-50 p-4 rounded-lg mb-6 w-full">
                  <p className="text-red-800 text-sm">
                    Error code: {orderStatus.failed_reason_code}
                  </p>
                </div>
              )}

              <div className="space-y-3 w-full">
                <Button onClick={handleTryAgain} className="w-full">
                  Try Again
                </Button>
                <Button variant="outline" onClick={handleGoToDashboard} className="w-full">
                  <Home className="mr-2 h-4 w-4" />
                  Go to Dashboard
                </Button>
              </div>
            </>
          ) : (
            <>
              <XCircle className="h-12 w-12 text-yellow-500 mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Payment Status Unknown</h2>
              <p className="text-gray-600 text-center mb-6">
                We couldn't determine the final status of your payment.
              </p>
              <div className="space-y-3 w-full">
                <Button onClick={handleGoToDashboard} className="w-full">
                  <Home className="mr-2 h-4 w-4" />
                  Go to Dashboard
                </Button>
                <Button variant="outline" onClick={handleTryAgain} className="w-full">
                  Try Again
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default PaymentSuccess;
