import { createContext, useContext, useState, type ReactNode } from 'react';

export type VerificationStatus = 'Pending Verification' | 'Verification In Progress' | 'Verified / Accepted' | 'Rejected';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'PENDING';

export interface VerificationRequest {
  id: string; // Token Number
  visitorName: string;
  documentType: string;
  documentSource: 'Upload' | 'Camera Scan';
  status: VerificationStatus;
  risk: RiskLevel;
  priority: 'Normal' | 'High';
  documentImage?: string; // Data URL
  faceImage?: string; // Data URL for live face
  details: {
    fullName?: string;
    dob?: string;
    nationality?: string;
    passportNumber?: string;
    digiLockerConnected?: boolean;
  };
  rejectionReason?: string;
  createdAt: string;
  submittedAt: string;
  verificationStartedAt?: string;
  verifiedAt?: string;
  rejectedAt?: string;
}

export interface VisitorProfile {
  mobile: string;
  email: string;
  digiLockerConnected?: boolean;
}

export interface AppNotification {
  id: string;
  role: 'VISITOR' | 'FORCE';
  title: string;
  message: string;
  time: string;
  read: boolean;
  linkTo?: string; // e.g. token id
}

interface VerificationContextType {
  requests: VerificationRequest[];
  visitorProfile: VisitorProfile | null;
  notifications: AppNotification[];
  updateVisitorProfile: (profile: VisitorProfile) => void;
  clearSession: () => void;
  addNotification: (notification: Omit<AppNotification, 'id' | 'read' | 'time'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: (role: 'VISITOR' | 'FORCE') => void;
  addRequest: (req: Omit<VerificationRequest, 'id' | 'status' | 'risk' | 'priority' | 'createdAt' | 'submittedAt'>) => string;
  updateStatus: (id: string, status: VerificationStatus, reason?: string) => void;
  updateRisk: (id: string, risk: RiskLevel) => void;
  updateFaceImage: (id: string, image: string) => void;
  getRequest: (id: string) => VerificationRequest | undefined;
}

const VerificationContext = createContext<VerificationContextType | undefined>(undefined);

export function VerificationProvider({ children }: { children: ReactNode }) {
  const [visitorProfile, setVisitorProfile] = useState<VisitorProfile | null>(null);

  const [notifications, setNotifications] = useState<AppNotification[]>([]);

  const [requests, setRequests] = useState<VerificationRequest[]>([]);

  const clearSession = () => {
    setVisitorProfile(null);
    setRequests([]);
    setNotifications([]);
  };

  const addNotification = (notif: Omit<AppNotification, 'id' | 'read' | 'time'>) => {
    setNotifications(prev => [{
      ...notif,
      id: Math.random().toString(36).substr(2, 9),
      read: false,
      time: new Date().toISOString()
    }, ...prev]);
  };

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllAsRead = (role: 'VISITOR' | 'FORCE') => {
    setNotifications(prev => prev.map(n => n.role === role ? { ...n, read: true } : n));
  };

  const updateVisitorProfile = (profile: VisitorProfile) => {
    setVisitorProfile(profile);
    addNotification({
      role: 'VISITOR',
      title: 'Profile Updated',
      message: 'Your contact information has been updated successfully.'
    });
    addNotification({
      role: 'FORCE',
      title: 'Visitor Profile Updated',
      message: 'Rahul Sharma has updated their contact information.'
    });
  };

  const addRequest = (req: Omit<VerificationRequest, 'id' | 'status' | 'risk' | 'priority' | 'createdAt' | 'submittedAt'>) => {
    const id = `IND-${Math.floor(100000 + Math.random() * 900000)}`;
    const timestamp = new Date().toISOString();
    const newReq: VerificationRequest = {
      ...req,
      id,
      status: 'Pending Verification',
      risk: 'PENDING',
      priority: 'Normal',
      createdAt: timestamp,
      submittedAt: timestamp
    };
    setRequests(prev => [newReq, ...prev]);

    addNotification({
      role: 'VISITOR',
      title: 'Document Submitted',
      message: `Your document for ${req.documentType} was submitted successfully.`,
      linkTo: id
    });
    addNotification({
      role: 'FORCE',
      title: 'New Verification Request',
      message: `Token ${id} has been submitted by ${req.visitorName}.`,
      linkTo: id
    });

    return id;
  };

  const updateStatus = (id: string, status: VerificationStatus, reason?: string) => {
    const timestamp = new Date().toISOString();
    setRequests(prev => prev.map(req => {
      if (req.id !== id) return req;
      const updated = { ...req, status, rejectionReason: reason };
      if (status === 'Verification In Progress' && !updated.verificationStartedAt) {
        updated.verificationStartedAt = timestamp;
      } else if (status === 'Verified / Accepted') {
        updated.verifiedAt = timestamp;
        updated.risk = 'LOW';
      } else if (status === 'Rejected') {
        updated.rejectedAt = timestamp;
      }
      return updated;
    }));

    if (status === 'Verification In Progress') {
      addNotification({ role: 'VISITOR', title: 'Verification Started', message: `Force has started verifying your request ${id}.`, linkTo: id });
    } else if (status === 'Verified / Accepted') {
      addNotification({ role: 'VISITOR', title: 'Verification Accepted', message: `Your verification request ${id} has been approved.`, linkTo: id });
      addNotification({ role: 'FORCE', title: 'Verification Completed', message: `You approved token ${id}.`, linkTo: id });
    } else if (status === 'Rejected') {
      addNotification({ role: 'VISITOR', title: 'Verification Rejected', message: `Your request ${id} was rejected. Reason: ${reason}`, linkTo: id });
      addNotification({ role: 'FORCE', title: 'Verification Rejected', message: `You rejected token ${id}.`, linkTo: id });
    }
  };

  const updateRisk = (id: string, risk: RiskLevel) => {
    setRequests(prev => prev.map(req => req.id === id ? { ...req, risk } : req));
  };

  const updateFaceImage = (id: string, image: string) => {
    setRequests(prev => prev.map(req => req.id === id ? { ...req, faceImage: image } : req));
  };

  const getRequest = (id: string) => requests.find(req => req.id === id);

  return (
    <VerificationContext.Provider value={{ 
      requests, visitorProfile, notifications, 
      updateVisitorProfile, clearSession, 
      addNotification, markAsRead, markAllAsRead, 
      addRequest, updateStatus, updateRisk, updateFaceImage, getRequest 
    }}>
      {children}
    </VerificationContext.Provider>
  );
}

export function useVerification() {
  const context = useContext(VerificationContext);
  if (context === undefined) {
    throw new Error('useVerification must be used within a VerificationProvider');
  }
  return context;
}
