from src.api import users, posts, hashtags, gemini, ai_agents

router.include_router(users.router)
router.include_router(posts.router)
router.include_router(hashtags.router)
router.include_router(gemini.router)
router.include_router(ai_agents.router) 