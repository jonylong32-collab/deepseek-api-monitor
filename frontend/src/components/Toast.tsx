/** Toast 通知组件 */
import './Toast.css';

interface Props {
  message: string;
  type?: 'success' | 'error' | 'info';
}

export default function Toast({ message, type = 'info' }: Props) {
  return (
    <div className={`toast toast-${type}`}>
      <span className="toast-icon">
        {type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}
      </span>
      <span className="toast-message">{message}</span>
    </div>
  );
}
