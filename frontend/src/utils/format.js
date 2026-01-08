/**
 * 修正封面图片路径，将后端返回的相对路径转换为可访问的URL
 * @param {string} path - 从后端获取的封面路径
 * @returns {string} - 完整的可访问URL
 */
export const fixCoverPath = (path) => {
  if (!path || typeof path !== 'string') {
    return '';
  }
  
  let fixedPath = path.replace(/\\/g, '/');
  const backendBaseUrl = 'http://localhost:5000';
  
  if (fixedPath.startsWith('/')) {
    fixedPath = `${backendBaseUrl}${fixedPath}`;
  } else if (!fixedPath.startsWith('http')) {
    fixedPath = `${backendBaseUrl}/${fixedPath}`;
  }
  
  return fixedPath;
};