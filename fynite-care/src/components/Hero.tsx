import React from 'react';
import {
  ArrowRight,
  Stethoscope,
  ShieldCheck,
  Clock,
  Star
} from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <section className="w-full bg-white px-8 sm:px-12 md:px-[60px] pt-[35px] pb-[45px]">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-4 items-center">
        {/* ===================================================================
            LEFT COLUMN (~55% width)
            =================================================================== */}
        <div className="lg:col-span-7 flex flex-col items-start pr-0 lg:pr-6 z-10">
          {/* Badge Pill: Heart-with-pulse icon + "Smart Healthcare, Just for You" */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#F2F6E8] border border-[#DCE6C8] text-[#76A63F] text-[14px] font-medium mb-[30px] shadow-sm">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#76A63F"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              <path d="M3.22 12H9.5l1.5-3 2 6 1.5-3h6.28" />
            </svg>
            <span>Smart Healthcare, Just for You</span>
          </div>

          {/* Heading H1 (72px, 1.15 line-height, -1.5px tracking) */}
          <h1 className="text-[48px] sm:text-[60px] lg:text-[72px] leading-[1.14] font-bold text-[#0A0A0A] tracking-[-1.5px] mb-[22px]">
            Your Health,<br />
            Our <span className="text-[#76A63F]">Priority</span>
          </h1>

          {/* Subtitle Paragraph (20px, 1.5 line-height, #2E2E2E) */}
          <p className="text-[17px] sm:text-[20px] leading-[1.5] text-[#2E2E2E] font-normal max-w-[420px] mb-[30px]">
            Advanced technology and compassionate care come together to deliver a healthier, happier you.
          </p>

          {/* Buttons Row (gap 16px) */}
          <div className="flex flex-wrap items-center gap-4 mb-[36px]">
            {/* Primary Button */}
            <button className="btn-arrow-slide group h-[50px] pl-6 pr-2 py-2 rounded-full bg-[#76A63F] hover:bg-[#648F33] text-white flex items-center gap-3.5 shadow-[0_4px_16px_rgba(118,166,63,0.3)] transition-all duration-200 cursor-pointer">
              <span className="text-[15px] font-medium tracking-tight">Book a Schedule</span>
              <span className="arrow-icon-circle w-[34px] h-[34px] rounded-full bg-white flex items-center justify-center text-[#76A63F] transition-all duration-200 shadow-sm">
                <ArrowRight size={15} strokeWidth={2.4} />
              </span>
            </button>

            {/* Secondary Button */}
            <button className="h-[50px] px-7 rounded-full bg-white border border-[#9DBB74] hover:bg-[#F2F6E8]/60 text-[#0A0A0A] text-[15px] font-medium transition-all duration-200 cursor-pointer shadow-sm">
              Explore Services
            </button>
          </div>

          {/* Social Proof Row: 4 overlapping avatars + 4K+ Trusted by Thousands */}
          <div className="flex items-center">
            {/* Avatars */}
            <div className="flex items-center -space-x-[10px]">
              <img
                src="/images/avatar1.jpg"
                alt="Patient"
                className="w-[36px] h-[36px] rounded-full border-2 border-white object-cover shadow-sm"
              />
              <img
                src="/images/avatar2.jpg"
                alt="Patient"
                className="w-[36px] h-[36px] rounded-full border-2 border-white object-cover shadow-sm"
              />
              <img
                src="/images/avatar3.jpg"
                alt="Patient"
                className="w-[36px] h-[36px] rounded-full border-2 border-white object-cover shadow-sm"
              />
              <img
                src="/images/avatar4.jpg"
                alt="Patient"
                className="w-[36px] h-[36px] rounded-full border-2 border-white object-cover shadow-sm"
              />
            </div>

            {/* Text details */}
            <div className="ml-3.5 flex flex-col justify-center leading-tight">
              <span className="text-[18px] font-bold text-[#76A63F]">4K+</span>
              <span className="text-[13px] font-normal text-[#6B6B6B]">Trusted by Thousands</span>
            </div>
          </div>
        </div>

        {/* ===================================================================
            RIGHT COLUMN (~45% width): Hero Image Panel + Floating Glass Cards
            =================================================================== */}
        <div className="lg:col-span-5 flex justify-center lg:justify-end relative mt-6 lg:mt-0">
          {/* Main Hero Panel Box (~440px wide x ~520px tall, rounded 40px) */}
          <div className="relative w-full max-w-[440px] h-[520px] rounded-[40px] bg-gradient-to-b from-[#E6F6D2] to-[#F6FCEC] border border-[#DCE6C8] shadow-[0_10px_30px_rgba(0,0,0,0.06)] overflow-hidden">
            {/* Halftone dot pattern overlay in top-left */}
            <div className="absolute inset-0 halftone-overlay pointer-events-none" />

            {/* Clean Doctor Photo */}
            <img
              src="/images/doctor.jpg"
              alt="Doctor smiling in white coat with stethoscope"
              className="absolute inset-0 w-full h-full object-cover select-none pointer-events-none"
            />
          </div>

          {/* =================================================================
              FLOATING GLASS CARD #1 (Top-Left, overlapping left edge by ~48px)
              Width: ~126px, rounded 14px, green border 1.5px
              ================================================================= */}
          <div className="animate-float-1 absolute -left-[30px] sm:-left-[48px] top-[64px] w-[126px] rounded-[14px] bg-white/75 backdrop-blur-[12px] border-[1.5px] border-[#76A63F]/70 shadow-[0_10px_25px_rgba(0,0,0,0.08)] p-2.5 z-20">
            <div className="flex flex-col gap-2">
              {/* Row 1: Expert Doctors */}
              <div className="flex items-center gap-2 pb-2 border-b border-dashed border-[#DADADA]">
                <div className="w-[24px] h-[24px] rounded-full border border-[#76A63F] flex items-center justify-center text-[#76A63F] shrink-0 bg-white/60">
                  <Stethoscope size={12} strokeWidth={2} />
                </div>
                <span className="text-[11px] font-semibold text-[#0A0A0A] leading-tight">
                  Expert Doctors
                </span>
              </div>

              {/* Row 2: Advanced Technology */}
              <div className="flex items-center gap-2 pb-2 border-b border-dashed border-[#DADADA]">
                <div className="w-[24px] h-[24px] rounded-full border border-[#76A63F] flex items-center justify-center text-[#76A63F] shrink-0 bg-white/60">
                  <ShieldCheck size={12} strokeWidth={2} />
                </div>
                <span className="text-[11px] font-semibold text-[#0A0A0A] leading-tight">
                  Advanced Technology
                </span>
              </div>

              {/* Row 3: 24/7 Support */}
              <div className="flex items-center gap-2">
                <div className="w-[24px] h-[24px] rounded-full border border-[#76A63F] flex items-center justify-center text-[#76A63F] shrink-0 bg-white/60">
                  <Clock size={12} strokeWidth={2} />
                </div>
                <span className="text-[11px] font-semibold text-[#0A0A0A] leading-tight">
                  24/7 Support
                </span>
              </div>
            </div>
          </div>

          {/* =================================================================
              FLOATING GLASS CARD #2 (Right side, lower-middle, overlapping right by ~28px)
              Width: ~195px, rounded 14px, green border 1.5px
              ================================================================= */}
          <div className="animate-float-2 absolute -right-[20px] sm:-right-[28px] top-[285px] w-[195px] rounded-[14px] bg-white/75 backdrop-blur-[12px] border-[1.5px] border-[#76A63F]/70 shadow-[0_10px_25px_rgba(0,0,0,0.08)] p-3 z-20">
            {/* Doctor info row */}
            <div className="flex items-center gap-2">
              <img
                src="/images/doctor-nusrat.jpg"
                alt="Dr. Nusrat Rahman"
                className="w-[28px] h-[28px] rounded-full object-cover border border-white shrink-0 shadow-xs"
              />
              <div className="flex flex-col leading-tight">
                <span className="text-[12px] font-bold text-[#0A0A0A]">Dr. Nusrat Rahman</span>
                <span className="text-[10px] text-[#6B6B6B]">General Physician</span>
              </div>
            </div>

            {/* Rating row */}
            <div className="flex items-center gap-1.5 mt-2 mb-2">
              <Star size={12} className="text-[#76A63F] fill-[#76A63F]" />
              <span className="text-[11px] font-bold text-[#0A0A0A]">4.8</span>
              <span className="text-[10px] text-[#6B6B6B]">(179 Reviews)</span>
            </div>

            {/* Mini button */}
            <button className="w-full h-[22px] rounded-[8px] bg-[#76A63F] hover:bg-[#648F33] text-white text-[9px] font-medium flex items-center justify-center transition-colors duration-200 cursor-pointer shadow-xs">
              Book a Schedule
            </button>
          </div>

          {/* =================================================================
              FLOATING GLASS CARD #3 (Bottom-Left, overlapping bottom-left by ~30px)
              Width: ~195px, rounded 14px, green border 1.5px
              ================================================================= */}
          <div className="animate-float-3 absolute -left-[20px] sm:-left-[30px] bottom-[16px] w-[195px] rounded-[14px] bg-white/75 backdrop-blur-[12px] border-[1.5px] border-[#76A63F]/70 shadow-[0_10px_25px_rgba(0,0,0,0.08)] p-2.5 z-20">
            <div className="flex items-center justify-between gap-2">
              <div className="flex flex-col leading-tight">
                <span className="text-[11px] font-bold text-[#0A0A0A] mb-0.5">
                  Your Health Companion
                </span>
                <span className="text-[9px] text-[#6B6B6B] leading-tight">
                  Personalized care for every stage of your life.
                </span>
              </div>

              {/* Green circle with white heart in hands */}
              <div className="w-[32px] h-[32px] rounded-full bg-[#76A63F] flex items-center justify-center text-white shrink-0 shadow-sm">
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
