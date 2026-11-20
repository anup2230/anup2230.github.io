# The blog

Posts live in `blog/posts/` as markdown files. `blog/posts.json` lists them.
The live site publishes from the **prod** branch, so make blog changes there
(and on `main` too if you want the two branches to match).

## Edit a post

1. On GitHub, switch to the `prod` branch and open `blog/posts/<slug>.md`.
2. Click the pencil icon, make your changes, and commit.
3. The site updates in a minute or two.

To change a post's title, date or summary, edit its entry in `blog/posts.json`.

## Add a post

1. On the `prod` branch, open `blog/posts/` and choose **Add file → Create new file**.
2. Name it `my-new-post.md` (lowercase, dashes, no spaces) and write the post in markdown.
3. Open `blog/posts.json` and add an entry at the top. Keep the comma between entries:

```json
[
  {
    "slug": "my-new-post",
    "title": "My new post",
    "date": "2026-12-01",
    "summary": "One or two sentences that show up in the list."
  },
  {
    "slug": "no-paychecks-no-taxes",
    ...
  }
]
```

The `slug` must match the file name without `.md`. Posts are listed newest first by date,
and each one gets its own link: `https://anup2230.github.io/blog.html#my-new-post`.

## Markdown you can use

`## Heading`, `**bold**`, `*italic*`, `[link text](https://...)`, `- bullet`, `1. numbered`,
`> quote`, `` `code` ``, code blocks with three backticks, and images with `![alt](assets/img/file.jpg)`.

## Delete a post

Remove its file from `blog/posts/` and its entry from `blog/posts.json`.
