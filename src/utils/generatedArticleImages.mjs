function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function getGeneratedArticleImagePath(slug, imageId) {
  return `/images/generated/posts/${slug}/${imageId}.jpg`;
}

function getBlogSlugFromFile(filePath) {
  if (!filePath) {
    throw new Error('generated image marker could not determine the source markdown file');
  }

  const normalized = filePath.replaceAll('\\', '/');
  const marker = '/src/content/work/';
  const index = normalized.indexOf(marker);
  if (index === -1) {
    throw new Error(`generated image marker only supports blog content files, got: ${filePath}`);
  }

  return normalized.slice(index + marker.length).replace(/\.(md|mdx)$/i, '');
}

export function remarkGeneratedArticleImages() {
  return (tree, file) => {
    const frontmatter = file?.data?.astro?.frontmatter ?? file?.data?.frontmatter ?? {};
    const generatedImages = Array.isArray(frontmatter.generatedImages) ? frontmatter.generatedImages : [];

    if (generatedImages.length === 0) {
      return;
    }

    const slug = getBlogSlugFromFile(file.path);
    const imageMap = new Map(generatedImages.map((image) => [image.id, image]));
    const markerPattern = /^\[\[generated-image:([a-z0-9-]+)\]\]$/;

    function visit(node, parent) {
      if (!node || typeof node !== 'object') {
        return;
      }

      if (node.type === 'paragraph' && parent && Array.isArray(parent.children)) {
        const textContent = (node.children ?? [])
          .filter((child) => child.type === 'text')
          .map((child) => child.value)
          .join('')
          .trim();

        const match = textContent.match(markerPattern);
        if (match) {
          const imageId = match[1];
          const image = imageMap.get(imageId);

          if (!image) {
            throw new Error(
              `unknown generated image marker "${imageId}" in ${file.path}. Add it to frontmatter.generatedImages.`
            );
          }

          const src = getGeneratedArticleImagePath(slug, imageId);
          const caption = image.caption?.trim();
          const figure = [
            '<figure class="generated-article-image">',
            `  <img src="${escapeHtml(src)}" alt="${escapeHtml(image.alt)}" loading="lazy" />`,
            caption ? `  <figcaption>${escapeHtml(caption)}</figcaption>` : '',
            '</figure>',
          ]
            .filter(Boolean)
            .join('\n');

          const index = parent.children.indexOf(node);
          parent.children[index] = {
            type: 'html',
            value: figure,
          };
          return;
        }
      }

      if (Array.isArray(node.children)) {
        for (const child of node.children) {
          visit(child, node);
        }
      }
    }

    visit(tree, null);
  };
}
