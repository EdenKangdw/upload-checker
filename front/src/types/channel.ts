export interface ChannelInfo {
  channel_check_option_id: number;
  channel_check_type: "check";
  channel_code: string;
  channel_creator_id: number;
  channel_id: number;
  channel_name: string;
  channel_user_count:  number;
  created_at: string; // "2024-05-26T09:09:40"
  updated_at: string; // "2024-05-26T09:09:40"
}

export interface ChannelListItem {
  channel_id: number;
  channel_name: string;
  user_type: "CREATOR" | "MANAGER" | "MEMBER";
}

export interface GroupList {
  group_name: string;
  group_id: number;
  updated_at: string;
  created_at: string;
}

export interface getCheckPeriodList {
  checks: string[]; // 체크한 사람 이름 배열
  date: string;
}

export interface getMyCheckList {
  check: string; // O or X
  date: string;
}

export interface UserInfo {
  user_id: number;
  user_name: string; // 카톡이름
  user_nickname: string | null; // 설정한 닉네임
  updated_at: string;
  created_at: string;
}


