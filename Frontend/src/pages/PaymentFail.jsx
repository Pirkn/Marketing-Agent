import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { XCircle, Home, RefreshCw } from 'lucide-react';

function PaymentFail() {
  const navigate = useNavigate();

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  const handleTryAgain = () => {
    navigate('/payment');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <XCircle className="h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Payment Cancelled</h2>
          <p className="text-gray-600 text-center mb-6">
            Your payment was cancelled or could not be completed. No charges were made to your account.
          </p>

          <div className="bg-yellow-50 p-4 rounded-lg mb-6 w-full">
            <h3 className="font-semibold text-yellow-900 mb-2">What happened?</h3>
            <ul className="text-yellow-800 space-y-1 text-sm">
              <li>• You may have cancelled the payment</li>
              <li>• There might have been a technical issue</li>
              <li>• Your bank may have declined the transaction</li>
              <li>• The payment session may have expired</li>
            </ul>
          </div>

          <div className="space-y-3 w-full">
            <Button onClick={handleTryAgain} className="w-full">
              <RefreshCw className="mr-2 h-4 w-4" />
              Try Again
            </Button>
            <Button variant="outline" onClick={handleGoToDashboard} className="w-full">
              <Home className="mr-2 h-4 w-4" />
              Go to Dashboard
            </Button>
          </div>

          <p className="text-xs text-gray-500 text-center mt-6">
            Need help? Contact our support team for assistance.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export default PaymentFail;
