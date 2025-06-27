import { useEffect } from 'react';
import type { RefObject } from 'react';

/**
 * Custom hook for auto-scrolling a container element
 * Will automatically scroll to bottom whenever children change
 * Doesn't require cursor focus to scroll
 */
export function useAutoScroll(
  ref: RefObject<HTMLDivElement | null>, 
  dependencies: unknown[] = []
): void {
  useEffect(() => {
    if (ref.current) {
      // Use a slight delay to ensure content has rendered
      const timeoutId = setTimeout(() => {
        ref.current?.scrollTo({
          top: ref.current.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
      
      return () => clearTimeout(timeoutId);
    }
  // Re-run this effect whenever dependencies change
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencies, ref]);
}
