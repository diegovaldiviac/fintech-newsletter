import praw
from sources import Article
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT, REDDIT_SUBREDDITS, MAX_ARTICLES_PER_SOURCE
)

def fetch() -> list[Article]:
    """Fetches top posts from fintech-related subreddits."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("[Reddit] WARNING: No credentials configured, skipping.")
        return []

    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )

        articles = []

        for subreddit_name in REDDIT_SUBREDDITS:
            subreddit = reddit.subreddit(subreddit_name)

            for post in subreddit.top(time_filter="week", limit=MAX_ARTICLES_PER_SOURCE):
                # Solo posts con links externos (no self posts sin contenido)
                if post.is_self and not post.selftext:
                    continue
                # Filtrar posts con poco engagement
                if post.score < 20:
                    continue

                summary = post.selftext[:300] if post.is_self else post.title
                url = post.url if not post.is_self else f"https://reddit.com{post.permalink}"

                articles.append(Article(
                    title=post.title,
                    summary=summary,
                    url=url,
                    source=f"Reddit r/{subreddit_name}",
                    published_at=None,
                ))

        print(f"[Reddit] {len(articles)} posts obtenidos.")
        return articles

    except Exception as e:
        print(f"[Reddit] Error al hacer fetch: {e}")
        return []
