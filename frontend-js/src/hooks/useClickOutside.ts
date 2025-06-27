import { useEffect, useRef } from 'react';
import type { RefObject } from 'react';

type UseClickOutsideProps = {
  onClickOutside: () => void;
  enabled?: boolean;
};

/**
 * A hook that detects clicks outside of the specified element
 * and calls the provided callback function when detected
 * 
 * @param onClickOutside - Function to call when a click outside is detected
 * @param enabled - Whether the detection is enabled (default: true)
 * @returns - Ref to attach to the element that should be monitored
 */
function useClickOutside<T extends HTMLElement>({ 
  onClickOutside,
  enabled = true 
}: UseClickOutsideProps): RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!enabled) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        onClickOutside();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClickOutside, enabled]);

  return ref;
}

export default useClickOutside;
