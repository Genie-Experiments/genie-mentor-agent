import { SVG_PATHS } from '@/constant/answerTab';
import React from 'react';

interface StarIconProps {
  size?: number;
  color?: string;
  className?: string;
}

export const StarIcon: React.FC<StarIconProps> = ({
  size = 12,
  color = '#00A599',
  className = '',
}) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={Math.round((size * 11) / 12)}
    viewBox="0 0 12 11"
    fill="none"
    className={className}
  >
    <path d={SVG_PATHS.star} fill={color} />
  </svg>
);
