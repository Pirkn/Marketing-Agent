import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { PostsProvider } from "./contexts/PostsContext";
import { KarmaProvider } from "./contexts/KarmaContext";
import { LeadsProvider } from "./contexts/LeadsContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Sidebar from "./components/Sidebar";
import ScrollToTop from "./components/ScrollToTop";
import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Leads";
import ViralTemplates from "./pages/ViralTemplates";
import ViralTemplateEdit from "./pages/ViralTemplateEdit";
import Products from "./pages/Products";
import ProductAnalysis from "./pages/ProductAnalysis";
import RedditPosts from "./pages/RedditPosts";
import Posts from "./pages/Posts";
import Settings from "./pages/Settings";
import Karma from "./pages/Karma";
import SignIn from "./pages/SignIn";
import SignUp from "./pages/SignUp";
import ForgotPassword from "./pages/ForgotPassword";
import Homepage from "./pages/Homepage";
import Onboarding from "./pages/Onboarding";
import Payment from "./pages/Payment";
import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentFail from "./pages/PaymentFail";
import { useAuth } from "./contexts/AuthContext";
import { Navigate } from "react-router-dom";

// Component to handle root path redirects
const RootRedirect = () => {
  const { user } = useAuth();
  return user ? <Navigate to="/dashboard" replace /> : <Homepage />;
};

function App() {
  return (
    <AuthProvider>
      <PostsProvider>
        <LeadsProvider>
          <KarmaProvider>
            <Router>
              <ScrollToTop />
              <Routes>
                {/* Public routes */}
                <Route path="/" element={<RootRedirect />} />
                <Route path="/onboarding" element={<Onboarding />} />
                <Route path="/payment" element={<Payment />} />
                <Route path="/payment/success" element={<PaymentSuccess />} />
                <Route path="/payment/fail" element={<PaymentFail />} />
                <Route path="/signin" element={<SignIn />} />
                <Route path="/signup" element={<SignUp />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />

                {/* Protected routes */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <Dashboard />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/leads"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <Leads />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/viral-templates"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <ViralTemplates />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/viral-templates/:templateId"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <ViralTemplateEdit />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/products"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <Products />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/product-analysis"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <ProductAnalysis />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/reddit-posts"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <RedditPosts />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/posts"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <Posts />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/karma"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <Karma />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <div className="flex h-screen bg-gray-50">
                        <Sidebar />
                        <div className="flex-1 overflow-auto">
                          <Settings />
                        </div>
                      </div>
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </Router>
          </KarmaProvider>
        </LeadsProvider>
      </PostsProvider>
    </AuthProvider>
  );
}

export default App;
