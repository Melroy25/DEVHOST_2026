import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { WhyChooseUs } from './components/WhyChooseUs';

export default function App() {
  return (
    <div className="min-h-screen bg-[#EFEFEF] flex justify-center py-0 md:py-[60px] lg:py-[95px] px-0 sm:px-4">
      {/* Centered White Container (max-width ~1100px, no rounded corners) */}
      <div className="w-full max-w-[1100px] bg-white shadow-[0_20px_60px_rgba(0,0,0,0.12)] overflow-hidden flex flex-col">
        {/* Navbar */}
        <Navbar />

        {/* Hero Section */}
        <main className="flex-1">
          <Hero />
          {/* Why Choose Us Section */}
          <WhyChooseUs />
        </main>
      </div>
    </div>
  );
}
