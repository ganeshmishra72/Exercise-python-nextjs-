import Navbar from '@/components/Navbar'
import Hero from '@/components/Hero'
import Features from '@/components/Features'
import HowItWorks from '@/components/HowItWorks'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <main style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #020617, #0f172a)',
      color: 'white'
    }}>
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <Footer />
    </main>
  )
}