import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '学氧助手文档',
  description: '学氧助手 - AI 驱动的学习助手平台',
  base: '/',
  cleanUrls: true,

  sitemap: {
    hostname: 'https://docs.xueyang.me',
  },

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    // Open Graph
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: '学氧助手文档' }],
    ['meta', { property: 'og:description', content: '学氧助手 - AI 驱动的学习助手平台' }],
    ['meta', { property: 'og:image', content: 'https://docs.xueyang.me/og-image.png' }],
    ['meta', { property: 'og:url', content: 'https://docs.xueyang.me' }],
    ['meta', { property: 'og:site_name', content: '学氧助手文档' }],
    // Twitter Card
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: '学氧助手文档' }],
    ['meta', { name: 'twitter:description', content: '学氧助手 - AI 驱动的学习助手平台' }],
  ],

  themeConfig: {
    nav: [
      { text: '首页', link: 'https://xueyang.me' },
      { text: '学氧助手', link: 'https://learn.xueyang.me' },
    ],

    sidebar: [
      {
        text: '指南',
        items: [
          { text: '介绍', link: '/intro' },
          { text: '快速开始', link: '/quick-start' },
          { text: '部署指南', link: '/deployment' },
        ]
      },
      {
        text: '功能',
        items: [
          { text: 'AI 对话', link: '/features/chat' },
          { text: '编程练习', link: '/features/coding' },
          { text: '简历优化', link: '/features/resume' },
          { text: '笔记管理', link: '/features/notes' },
        ]
      },
      {
        text: '开发',
        items: [
          { text: '架构设计', link: '/dev/architecture' },
          { text: 'API 文档', link: '/dev/api' },
        ]
      },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/DAVINDAI/xueyang' },
    ],

    editLink: {
      pattern: 'https://github.com/DAVINDAI/xueyang/edit/main/frontend/docs/:path',
      text: '在 GitHub 上编辑此页',
    },

    footer: {
      message: '基于 VitePress 构建',
      copyright: `Copyright © 2024-${new Date().getFullYear()} 学氧助手`,
    },

    search: {
      provider: 'local',
    },
  },
})
