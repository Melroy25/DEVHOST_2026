export const WhyChooseUs: React.FC = () => {
  const features = [
    {
      title: 'Advanced Technology',
      description: 'Cutting-edge diagnostic and therapeutic platforms for optimal care.',
      icon: (
        <svg
          width="26"
          height="26"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#76A63F"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="3" />
          <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
          <path d="M4.93 4.93l2.12 2.12M16.95 16.95l2.12 2.12M4.93 19.07l2.12-2.12M16.95 7.05l2.12-2.12" />
        </svg>
      )
    },
    {
      title: 'Compassionate Care',
      description: 'Patient-centered clinical treatments guided by empathy and dedication.',
      icon: (
        <svg
          width="26"
          height="26"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#76A63F"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      )
    },
    {
      title: '24/7 Support',
      description: 'Around-the-clock medical consultations and continuous health monitoring.',
      icon: (
        <svg
          width="26"
          height="26"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#76A63F"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
          <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
        </svg>
      )
    }
  ];

  return (
    <section className="w-full bg-[#F5F7EF] px-8 sm:px-12 md:px-[60px] pt-[50px] pb-[80px]">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8 mb-4">
        {/* Left: Section Label */}
        <div className="shrink-0">
          <h2 className="text-[16px] font-medium text-[#76A63F] leading-snug">
            Why Choose Us
          </h2>
          <div className="w-[30px] h-[2.5px] bg-[#76A63F] rounded-full mt-1.5" />
        </div>

        {/* Right: Feature Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full lg:max-w-[780px]">
          {features.map((item, idx) => (
            <div
              key={idx}
              className="rounded-[24px] border-[1.5px] border-[#76A63F] bg-white/70 p-5 flex flex-col items-center text-center shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <div className="w-[46px] h-[46px] rounded-full border border-[#76A63F] flex items-center justify-center bg-white mb-3">
                {item.icon}
              </div>
              <h3 className="text-[14px] font-semibold text-[#0A0A0A] mb-1">
                {item.title}
              </h3>
              <p className="text-[11px] text-[#6B6B6B] leading-relaxed">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
