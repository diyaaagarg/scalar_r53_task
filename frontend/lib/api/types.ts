export interface SessionUser { id: string; email: string; display_name: string; }
export interface AwsAccount { aws_account_id: string; display_name: string; }
export interface Session { user: SessionUser; account: AwsAccount; region: string; }
export interface ApiError { error: { code: string; message: string; details: Array<{ field: string; message: string }> }; }
