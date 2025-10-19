import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

async def seed_courses():
    # Clear existing data
    await db.courses.delete_many({})
    await db.videos.delete_many({})
    
    # Sample courses
    courses = [
        {
            "id": str(uuid.uuid4()),
            "name": "Python Programming Basics",
            "description": "Learn Python programming from scratch with hands-on examples",
            "language": "english",
            "image_url": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Web Development Fundamentals",
            "description": "Master HTML, CSS, and JavaScript basics",
            "language": "english",
            "image_url": "https://images.unsplash.com/photo-1547658719-da2b51169166?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tamil: தமிழில் Python",
            "description": "தமிழில் Python நிரலாக்கம் கற்றுக்கொள்ளுங்கள்",
            "language": "tamil",
            "image_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Data Science with Python",
            "description": "Learn data analysis, visualization, and machine learning",
            "language": "english",
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "React Development",
            "description": "Build modern web applications with React",
            "language": "english",
            "image_url": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tamil: வலை மேம்பாடு",
            "description": "தமிழில் வலைதள உருவாக்கம் கற்றுக்கொள்ளுங்கள்",
            "language": "tamil",
            "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mobile App Development",
            "description": "Create cross-platform mobile applications",
            "language": "english",
            "image_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Database Management",
            "description": "Master SQL and database design principles",
            "language": "english",
            "image_url": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400&h=300&fit=crop",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.courses.insert_many(courses)
    print(f"Inserted {len(courses)} courses")
    
    # Create videos for each course (3 videos per course)
    for course in courses:
        videos = [
            {
                "id": str(uuid.uuid4()),
                "course_id": course["id"],
                "title": f"{course['name']} - Introduction",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "duration": 180,  # 3 minutes
                "order": 1
            },
            {
                "id": str(uuid.uuid4()),
                "course_id": course["id"],
                "title": f"{course['name']} - Core Concepts",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "duration": 240,  # 4 minutes
                "order": 2
            },
            {
                "id": str(uuid.uuid4()),
                "course_id": course["id"],
                "title": f"{course['name']} - Advanced Topics",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "duration": 150,  # 2.5 minutes
                "order": 3
            }
        ]
        await db.videos.insert_many(videos)
    
    print(f"Inserted {len(courses) * 3} videos")
    print("Database seeding completed!")

async def main():
    await seed_courses()
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
