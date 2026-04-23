'use client'

import styles from './Header.module.css'

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <span className={styles.logoIcon}>⚡</span>
        <span className={styles.logoText}>RepSense</span>
      </div>
      <p className={styles.tagline}>AI-Powered Exercise Form Detection</p>
      <div className={styles.badge}>
        <span className={styles.dot} />
        Live Model Active
      </div>
    </header>
  )
}