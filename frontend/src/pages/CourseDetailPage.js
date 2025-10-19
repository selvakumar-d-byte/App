import { useState, useEffect, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AuthContext } from "@/App";
import Header from "@/components/Header";
import AuthModal from "@/components/AuthModal";
import VideoPlayer from "@/components/VideoPlayer";
import CertificateModal from "@/components/CertificateModal";
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle, Lock, Play } from "lucide-react";
import { toast } from "sonner";

const CourseDetailPage = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [videos, setVideos] = useState([]);
  const [progress, setProgress] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showCertificate, setShowCertificate] = useState(false);
  const [certificate, setCertificate] = useState(null);
  const { user, token } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCourse();
    fetchVideos();
  }, [courseId]);

  useEffect(() => {
    if (user && token) {
      fetchProgress();
    }
  }, [user, token, courseId]);

  const fetchCourse = async () => {
    try {
      const response = await axios.get(`${API}/courses/${courseId}`);
      setCourse(response.data);
    } catch (error) {
      console.error("Failed to fetch course", error);
    }
  };

  const fetchVideos = async () => {
    try {
      const response = await axios.get(`${API}/courses/${courseId}/videos`);
      setVideos(response.data);
    } catch (error) {
      console.error("Failed to fetch videos", error);
    }
  };

  const fetchProgress = async () => {
    try {
      const response = await axios.get(
        `${API}/progress/user/${user.id}/course/${courseId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProgress(response.data);
    } catch (error) {
      console.error("Failed to fetch progress", error);
    }
  };

  const isVideoCompleted = (videoId) => {
    return progress.some(p => p.video_id === videoId && p.completed);
  };

  const getVideoProgress = (videoId) => {
    return progress.find(p => p.video_id === videoId);
  };

  const canPlayVideo = (video) => {
    if (!user) return false;
    
    const videoIndex = videos.findIndex(v => v.id === video.id);
    if (videoIndex === 0) return true;
    
    const previousVideo = videos[videoIndex - 1];
    return isVideoCompleted(previousVideo.id);
  };

  const handleVideoClick = (video) => {
    if (!user) {
      toast.error("Please login to watch videos");
      setShowAuthModal(true);
      return;
    }
    
    if (!canPlayVideo(video)) {
      toast.error("Please complete the previous video first");
      return;
    }
    
    setSelectedVideo(video);
  };

  const handleVideoComplete = async (videoId) => {
    await fetchProgress();
    
    // Check if all videos are completed
    const allCompleted = videos.every(v => 
      progress.some(p => p.video_id === v.id && p.completed) || v.id === videoId
    );
    
    if (allCompleted) {
      // Generate certificate
      try {
        const response = await axios.post(
          `${API}/certificates/generate?user_id=${user.id}&course_id=${courseId}`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setCertificate(response.data);
        setShowCertificate(true);
      } catch (error) {
        console.error("Failed to generate certificate", error);
      }
    }
  };

  if (!course) {
    return <div className="text-center py-16">Loading...</div>;
  }

  return (
    <div className="min-h-screen">
      <Header onAuthClick={() => setShowAuthModal(true)} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Course header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            {course.name}
          </h1>
          <p className="text-gray-300 text-lg">{course.description}</p>
        </div>
        
        {/* Video player */}
        {selectedVideo && (
          <div className="mb-8">
            <VideoPlayer
              video={selectedVideo}
              progress={getVideoProgress(selectedVideo.id)}
              onComplete={handleVideoComplete}
              userId={user?.id}
              courseId={courseId}
              token={token}
            />
          </div>
        )}
        
        {/* Videos list */}
        <div>
          <h2 className="text-2xl font-bold mb-6">Course Videos</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {videos.map((video, index) => {
              const completed = isVideoCompleted(video.id);
              const canPlay = canPlayVideo(video);
              
              return (
                <Card
                  key={video.id}
                  data-testid={`video-card-${video.id}`}
                  onClick={() => handleVideoClick(video)}
                  className={`bg-slate-800/50 border-slate-700 cursor-pointer transition-all ${
                    canPlay ? 'hover:border-cyan-500 hover:scale-105' : 'opacity-60 cursor-not-allowed'
                  }`}
                >
                  <CardContent className="p-4">
                    <div className="relative mb-3">
                      <div className="aspect-video bg-slate-700 rounded-lg flex items-center justify-center">
                        {completed ? (
                          <CheckCircle className="text-green-500" size={40} />
                        ) : canPlay ? (
                          <Play className="text-cyan-400" size={40} />
                        ) : (
                          <Lock className="text-gray-500" size={40} />
                        )}
                      </div>
                      <div className="absolute top-2 right-2 bg-black/70 px-2 py-1 rounded text-xs">
                        {Math.floor(video.duration / 60)}:{String(video.duration % 60).padStart(2, '0')}
                      </div>
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-1">{video.title}</h3>
                    <p className="text-gray-400 text-sm">Video {video.order}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </div>
      
      <AuthModal 
        open={showAuthModal} 
        onClose={() => setShowAuthModal(false)}
      />
      
      {certificate && (
        <CertificateModal
          open={showCertificate}
          onClose={() => setShowCertificate(false)}
          certificate={certificate}
        />
      )}
    </div>
  );
};

export default CourseDetailPage;