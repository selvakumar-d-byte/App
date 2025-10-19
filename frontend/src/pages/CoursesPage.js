import { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AuthContext } from "@/App";
import Header from "@/components/Header";
import AuthModal from "@/components/AuthModal";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Search } from "lucide-react";

const CoursesPage = () => {
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [search, setSearch] = useState("");
  const [language, setLanguage] = useState("");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCourses();
  }, []);

  useEffect(() => {
    filterCourses();
  }, [courses, search, language]);

  const fetchCourses = async () => {
    try {
      const response = await axios.get(`${API}/courses`);
      setCourses(response.data);
    } catch (error) {
      console.error("Failed to fetch courses", error);
    }
  };

  const filterCourses = () => {
    let filtered = courses;
    
    if (search) {
      filtered = filtered.filter(course => 
        course.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    if (language) {
      filtered = filtered.filter(course => 
        course.language.toLowerCase() === language.toLowerCase()
      );
    }
    
    setFilteredCourses(filtered);
  };

  const handleClear = () => {
    setSearch("");
    setLanguage("");
  };

  const handleCourseClick = (courseId) => {
    navigate(`/courses/${courseId}`);
  };

  return (
    <div className="min-h-screen">
      <Header onAuthClick={() => setShowAuthModal(true)} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Filter section */}
        <div className="mb-8 space-y-4">
          <h1 className="text-4xl font-bold mb-6" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>Available Courses</h1>
          
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <Input
                data-testid="search-input"
                type="text"
                placeholder="Search courses..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-gray-400"
              />
            </div>
            
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger data-testid="language-select" className="w-full sm:w-48 bg-slate-800/50 border-slate-700 text-white">
                <SelectValue placeholder="Select Language" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700 text-white">
                <SelectItem value="tamil">Tamil</SelectItem>
                <SelectItem value="english">English</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              data-testid="clear-btn"
              onClick={handleClear}
              variant="outline"
              className="border-slate-700 hover:bg-slate-800"
            >
              Clear
            </Button>
          </div>
        </div>
        
        {/* Courses grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredCourses.map((course) => (
            <Card
              key={course.id}
              data-testid={`course-card-${course.id}`}
              onClick={() => handleCourseClick(course.id)}
              className="bg-slate-800/50 border-slate-700 hover:border-cyan-500 transition-all cursor-pointer hover:scale-105"
            >
              <CardContent className="p-0">
                <img
                  src={course.image_url}
                  alt={course.name}
                  className="w-full h-48 object-cover rounded-t-lg"
                />
                <div className="p-4">
                  <h3 className="text-xl font-semibold text-white mb-2">{course.name}</h3>
                  <p className="text-gray-400 text-sm mb-2">{course.description}</p>
                  <span className="inline-block bg-cyan-500/20 text-cyan-400 px-3 py-1 rounded-full text-xs">
                    {course.language.charAt(0).toUpperCase() + course.language.slice(1)}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {filteredCourses.length === 0 && (
          <div className="text-center py-16">
            <p className="text-gray-400 text-lg">No courses found</p>
          </div>
        )}
      </div>
      
      <AuthModal 
        open={showAuthModal} 
        onClose={() => setShowAuthModal(false)}
      />
    </div>
  );
};

export default CoursesPage;