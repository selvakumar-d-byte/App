import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "@/App";
import Header from "@/components/Header";
import AuthModal from "@/components/AuthModal";
import { Button } from "@/components/ui/button";

const HomePage = () => {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleGetStarted = () => {
    if (user) {
      navigate("/courses");
    } else {
      setShowAuthModal(true);
    }
  };

  return (
    <div className="min-h-screen">
      <Header onAuthClick={() => setShowAuthModal(true)} />
      
      <div className="container mx-auto px-4 py-16">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
          {/* Left content */}
          <div className="flex-1 space-y-8">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
              Grow Your Skills With
              <br />
              <span className="text-cyan-400">LevelUpHive</span>
            </h1>
            
            <p className="text-lg text-gray-300 max-w-2xl">
              Learn programming, web development, data analytics and more – in Tamil and English. Step-by-step structured courses to help you master real-world skills.
            </p>
            
            <Button
              data-testid="get-started-btn"
              onClick={handleGetStarted}
              className="bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-6 text-lg rounded-lg transition-all hover:scale-105"
            >
              Get Started
            </Button>
          </div>
          
          {/* Right image */}
          <div className="flex-1 max-w-xl">
            <img
              src="https://customer-assets.emergentagent.com/job_974a39d1-ca80-4450-87b4-d897e29e4b54/artifacts/57abz271_main%20screen.png"
              alt="Skills Development"
              className="w-full rounded-2xl shadow-2xl"
            />
          </div>
        </div>
      </div>
      
      <footer className="text-center py-8 text-gray-400">
        <p>© LevelUpHive – built by Selvakumar</p>
      </footer>
      
      <AuthModal 
        open={showAuthModal} 
        onClose={() => setShowAuthModal(false)}
        onSuccess={() => {
          setShowAuthModal(false);
          navigate("/courses");
        }}
      />
    </div>
  );
};

export default HomePage;