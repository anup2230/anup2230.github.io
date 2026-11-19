# Writing a post

1. Add a markdown file to `blog/posts/`, for example `blog/posts/my-first-post.md`.
2. Add an entry for it at the top of `blog/posts.json`:

```json
[
  {
    "slug": "my-first-post",
    "title": "My first post",
    "date": "2026-11-20",
    "summary": "One or two sentences that show up in the list."
  }
]
```

The `slug` must match the file name without `.md`. Posts are listed newest first by date.
Each post gets its own link: `https://anup2230.github.io/blog.html#my-first-post`.
