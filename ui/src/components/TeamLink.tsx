import Link from 'next/link';
import { createTeamLink } from '@/utils/teamUtils';

interface TeamLinkProps {
  teamName: string;
  className?: string;
  children?: React.ReactNode;
}

export default function TeamLink({ teamName, className = '', children }: TeamLinkProps) {
  const teamUrl = createTeamLink(teamName);
  
  return (
    <Link href={teamUrl} className={`team-link ${className}`}>
      {children || teamName}
    </Link>
  );
}