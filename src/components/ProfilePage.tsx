import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Icon from "@/components/ui/icon";
import { useNavigate } from "react-router-dom";

interface ProfilePageProps {
  userData: any;
  onLogout: () => void;
}

const ProfilePage = ({ userData, onLogout }: ProfilePageProps) => {
  const navigate = useNavigate();
  
  const subscription = userData?.subscription || {};
  const subscriptionType = subscription.subscription_type || 'free';
  const endDate = subscription.end_date ? new Date(subscription.end_date).toLocaleDateString('ru-RU') : 'Не указана';
  
  const getSubscriptionBadge = () => {
    switch (subscriptionType) {
      case 'premium':
        return <Badge className="bg-gradient-to-r from-purple-500 to-pink-500">Premium</Badge>;
      case 'pro':
        return <Badge className="bg-gradient-to-r from-blue-500 to-cyan-500">Pro</Badge>;
      default:
        return <Badge variant="secondary">Free</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 p-4">
      <div className="max-w-2xl mx-auto py-8">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="mb-6"
        >
          <Icon name="ArrowLeft" size={20} className="mr-2" />
          Назад
        </Button>

        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-400 to-purple-400 flex items-center justify-center text-white text-2xl font-bold">
                  {userData?.name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div>
                  <CardTitle className="text-2xl">{userData?.name || 'Пользователь'}</CardTitle>
                  <CardDescription>{userData?.email}</CardDescription>
                </div>
              </div>
              {getSubscriptionBadge()}
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">ID пользователя</p>
                <p className="font-mono text-sm bg-muted p-2 rounded">{userData?.user_id}</p>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground mb-1">Дата окончания подписки</p>
                <p className="font-medium">{endDate}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Доступные функции</CardTitle>
            <CardDescription>Ваши текущие возможности в приложении</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-3">
                  <Icon name="Heart" size={20} className="text-pink-500" />
                  <span className="font-medium">Флирт режим</span>
                </div>
                {subscription.flirt ? (
                  <Badge className="bg-green-500">Активен</Badge>
                ) : (
                  <Badge variant="secondary">Недоступен</Badge>
                )}
              </div>

              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-3">
                  <Icon name="Flame" size={20} className="text-red-500" />
                  <span className="font-medium">Интим режим</span>
                </div>
                {subscription.intimate ? (
                  <Badge className="bg-green-500">Активен</Badge>
                ) : (
                  <Badge variant="secondary">Недоступен</Badge>
                )}
              </div>

              <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-3">
                  <Icon name="Crown" size={20} className="text-yellow-500" />
                  <span className="font-medium">Premium функции</span>
                </div>
                {subscription.premium ? (
                  <Badge className="bg-green-500">Активны</Badge>
                ) : (
                  <Badge variant="secondary">Недоступны</Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Настройки аккаунта</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start"
            >
              <Icon name="CreditCard" size={20} className="mr-3" />
              Управление подпиской
            </Button>
            
            <Button 
              variant="outline" 
              className="w-full justify-start"
            >
              <Icon name="Settings" size={20} className="mr-3" />
              Настройки
            </Button>
            
            <Button 
              variant="destructive" 
              className="w-full justify-start"
              onClick={onLogout}
            >
              <Icon name="LogOut" size={20} className="mr-3" />
              Выйти из аккаунта
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage;