import { Avatar } from 'primereact/avatar';

import { useUser } from '../contexts/UserContext';

function UserDetails() {
    const { user } = useUser();

    return (
        <div className="user-details" style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            gap: '10px'
        }}>
            <p>{user?.name}</p>
            <Avatar shape="circle" size="large" image={user?.details?.picture} />
        </div>
    );
}

export default UserDetails;