import { useEffect } from 'react'
import Hero from '../components/landing/Hero'
import FeatureStrip from '../components/landing/FeatureStrip'
import HowItWorks from '../components/landing/HowItWorks'
import Pathways from '../components/landing/Pathways'
import SystemsShowcase from '../components/landing/SystemsShowcase'
import Testimonials from '../components/landing/Testimonials'
import Faq from '../components/landing/Faq'
import CtaBanner from '../components/landing/CtaBanner'

export default function Home() {
  useEffect(() => {
    document.title = 'ROOT 404 — Elite Coder Platform'
  }, [])

  return (
    <>
      <Hero />
      <FeatureStrip />
      <HowItWorks />
      <Pathways />
      <SystemsShowcase />
      <Testimonials />
      <Faq />
      <CtaBanner />
    </>
  )
}
