import { useState } from 'react';
import { ArrowRight } from 'lucide-react';

export const Navbar = () => {
  const [activeNav, setActiveNav] = useState('Home');

  const navItems = ['Home', 'Services', 'Technology', "FAQ's", 'Contact us'];

  return (
    <header className="w-full bg-white">
      <div className="h-[85px] px-8 sm:px-12 md:px-[60px] flex items-center justify-between">
        {/* Left: Logo */}
        <a href="#" className="flex items-center gap-2 group">
          {/* Green plus/cross with leaves beneath */}
          <div className="w-[30px] h-[30px] flex items-center justify-center relative">
            <svg
              width="28"
              height="28"
              viewBox="0 0 32 32"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="transition-transform duration-200 group-hover:scale-105"
            >
              {/* Medical cross */}
              <rect x="13.5" y="4" width="5" height="15" rx="2" fill="#76A63F" />
              <rect x="8.5" y="9" width="15" height="5" rx="2" fill="#76A63F" />
              {/* Left Leaf */}
              <path
                d="M16 26C16 26 11 25 8.5 20.5C6.5 16.5 9.5 14 12 15C14.5 16 15.5 19.5 16 26Z"
                fill="#76A63F"
              />
              {/* Right Leaf */}
              <path
                d="M16 26C16 26 21 25 23.5 20.5C25.5 16.5 22.5 14 20 15C17.5 16 16.5 19.5 16 26Z"
                fill="#76A63F"
              />
            </svg>
          </div>
          <div className="text-[24px] font-semibold tracking-tight leading-none">
            <span className="text-[#0A0A0A]">Fynite</span>
            <span className="text-[#76A63F]">Care</span>
          </div>
        </a>

        {/* Center: Nav links */}
        <nav className="hidden md:flex items-center gap-[30px]">
          {navItems.map((item) => {
            const isActive = activeNav === item;
            return (
              <button
                key={item}
                onClick={() => setActiveNav(item)}
                className={`relative text-[14px] font-medium transition-colors duration-200 cursor-pointer ${
                  isActive ? 'text-[#0A0A0A] font-semibold' : 'text-[#6B6B6B] hover:text-[#0A0A0A]'
                }`}
              >
                <span>{item}</span>
                {isActive && (
                  <span className="absolute -bottom-[8px] left-1/2 -translate-x-1/2 w-[5px] h-[5px] bg-[#76A63F] rounded-full" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Right: "Book a Schedule" button */}
        <div className="flex items-center">
          <button className="btn-arrow-slide group flex items-center gap-3 pl-5 pr-2 py-2 rounded-full bg-white border-[1.5px] border-[#76A63F] shadow-[0_0_0_3px_rgba(118,166,63,0.15)] hover:shadow-[0_0_0_4px_rgba(118,166,63,0.25)] transition-all duration-200 cursor-pointer">
            <span className="text-[14px] font-medium text-[#0A0A0A] tracking-tight">
              Book a Schedule
            </span>
            <span className="arrow-icon-circle w-[28px] h-[28px] rounded-full bg-[#76A63F] group-hover:bg-[#648F33] flex items-center justify-center text-white transition-all duration-200">
              <ArrowRight size={14} strokeWidth={2.2} />
            </span>
          </button>
        </div>
      </div>

      {/* Divider line under navbar: 1px light gray #DADADA, inset ~60px from each side */}
      <div className="px-8 sm:px-12 md:px-[60px]">
        <div className="w-full h-[1px] bg-[#DADADA]" />
      </div>
    </header>
  );
};
