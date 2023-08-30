import React from 'react';

const ErrorComponent = ({ message }) => {
    return (
        <div className="error">
            <p>Error: {message}</p>
        </div>
    );
}

export default ErrorComponent;
