const isProd = import.meta.env.PROD;

export const API_BASE_URL = isProd ?
    import.meta.env.VITE_API_BASE_URL_PROD :
    'http://localhost:8000';

/**
 * @param {string} hyphenatedDate - date in "YYYY-MM-DD" format
 *   to be interpreted in local time
 * @return {string} a string formatted in the user's locale
 */
export const formatDate = (hyphenatedDate: string): string => {
  const [yyyy, mm, dd] = hyphenatedDate.split('-').map(Number);
  return new Date(yyyy, mm - 1, dd).toLocaleDateString();
};
