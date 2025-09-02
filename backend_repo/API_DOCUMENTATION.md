# Posts API Documentation

## Overview
This API provides endpoints for retrieving posts with their associated comments, designed to support infinite scrolling functionality on the frontend.

## Endpoints

### GET /api/posts/

Retrieves a paginated list of posts ordered by timestamp (latest first).

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number for pagination |
| `page_size` | integer | 10 | Number of posts per page (max: 100) |

#### Response Format

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "text": "This is a sample post",
      "timestamp": "2025-01-27T10:30:00Z",
      "author": {
        "username": "john_doe"
      },
      "comment_count": 5,
      "latest_comments": [
        {
          "id": "987fcdeb-51a2-43d1-9f12-123456789abc",
          "text": "Great post!",
          "timestamp": "2025-01-27T11:00:00Z",
          "author": {
            "username": "jane_smith"
          }
        },
        {
          "id": "456789ab-cdef-1234-5678-9abcdef01234",
          "text": "I agree with this",
          "timestamp": "2025-01-27T10:45:00Z",
          "author": {
            "username": "bob_wilson"
          }
        }
      ]
    }
  ]
}
```

#### Response Fields

**Post Fields:**
- `id`: Unique identifier for the post (UUID)
- `text`: Content of the post
- `timestamp`: When the post was created (ISO 8601 format)
- `author.username`: Username of the post author
- `comment_count`: Total number of comments on this post
- `latest_comments`: Array of up to 3 most recent comments

**Comment Fields:**
- `id`: Unique identifier for the comment (UUID)
- `text`: Content of the comment
- `timestamp`: When the comment was created (ISO 8601 format)
- `author.username`: Username of the comment author

#### Example Usage

```bash
# Get first page of posts
curl "http://localhost:8000/api/posts/"

# Get second page with custom page size
curl "http://localhost:8000/api/posts/?page=2&page_size=5"

# Get posts for infinite scrolling (frontend implementation)
fetch('/api/posts/?page=1&page_size=10')
  .then(response => response.json())
  .then(data => {
    // data.results contains the posts
    // data.next contains URL for next page (null if last page)
    // Use data.next to load more posts as user scrolls
  });
```

## Implementation Notes

### Performance Optimizations
- Uses `select_related()` to minimize database queries for user data
- Uses `prefetch_related()` with custom `Prefetch` to efficiently load comments
- Limits comments to 3 per post to control response size

### Infinite Scrolling Integration
- Standard pagination format compatible with most frontend infinite scroll libraries
- `next` field provides URL for the next page of results
- `count` field shows total number of posts available

### Database Queries
The endpoint is optimized to minimize N+1 query problems:
1. One query to fetch posts with authors
2. One query to fetch comments with their authors (prefetched)
3. Total: 2 database queries regardless of number of posts/comments

## Follow-up: Random Comments Implementation

To fetch 3 random comments instead of latest comments, modify the `get_latest_comments` method in `PostSerializer`:

```python
def get_latest_comments(self, obj):
    """Get up to 3 random comments for this post"""
    random_comments = obj.comments.select_related('user').order_by('?')[:3]
    return CommentSerializer(random_comments, many=True).data
```

**Note:** Using `order_by('?')` for randomization can be expensive on large datasets. For production use with many comments, consider alternative approaches like application-level sampling or database-specific random functions.