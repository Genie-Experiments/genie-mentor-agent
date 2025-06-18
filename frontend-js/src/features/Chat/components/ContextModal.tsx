import React from 'react';

interface ContextModalProps {
  isVisible: boolean;
  title: string;
  content: string;
  onClose: () => void;
}

const ContextModal: React.FC<ContextModalProps> = ({ isVisible, title, content, onClose }) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {' '}
      <div
        className="animate-slide-in-right h-full w-[450px] overflow-auto bg-white shadow-xl"
        style={{
          transition: 'transform 0.3s ease-out',
          borderRadius: '20px 0px 0px 20px',
        }}
      >
        <div
          className="sticky top-0 z-10 flex items-center justify-between bg-white px-[30px] py-[28.5px]"
          style={{ borderBottom: '1px solid #9CBFBC' }}
        >
          <h2
            style={{
              color: '#002835',
              fontFamily: 'Inter',
              fontSize: '18px',
              fontWeight: 600,
            }}
          >
            {title || 'Context Details'}
          </h2>{' '}
          <button onClick={onClose} className="flex cursor-pointer items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
              viewBox="0 0 30 30"
              fill="none"
              className="cursor-pointer"
            >
              <path
                d="M8 23.75L6.25 22L13.25 15L6.25 8L8 6.25L15 13.25L22 6.25L23.75 8L16.75 15L23.75 22L22 23.75L15 16.75L8 23.75Z"
                fill="#1D1B20"
              />
            </svg>
          </button>
        </div>{' '}
        <div
          className="px-[30px] py-[30px] whitespace-pre-wrap"
          style={{
            color: '#002835',
            fontFamily: 'Inter',
            fontSize: '16px',
            fontStyle: 'normal',
            fontWeight: 400,
            lineHeight: '24px',
          }}
        >
          {content}
        </div>
      </div>
    </div>
  );
};

export default ContextModal;
