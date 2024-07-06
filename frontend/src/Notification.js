import React from 'react';
import './Notification.css'

function Notification (props) {
    return (props.trigger) ? (
        <div className='Notification'>
            <div className='NotificationInner'>
                {props.children}
                
            </div>
        </div>
    ) : '';
}
export default Notification;