import {
  Body,
  Column,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Preview,
  Row,
  Section,
  Text,
} from '@react-email/components';

interface OrderItem {
  name: string;
  quantity: number;
}

interface OrderConfirmationEmailProps {
  user_name?: string;
  order_number?: string;
  total?: number;
  items?: OrderItem[];
}

export const OrderConfirmationEmail = ({
  user_name = 'User',
  order_number = 'ORD-12345',
  total = 120500,
  items = [
    { name: 'Sample product', quantity: 1 },
    { name: 'Another product', quantity: 2 },
  ],
}: OrderConfirmationEmailProps) => {

  return (
    <Html>
      <Head />
      <Preview>Your order {order_number} has been confirmed</Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Logo */}
          <Section style={logoSection}>
            <Img
              src="https://crushme.com.co/static/frontend/BUY.png"
              width="120"
              height="120"
              alt="CrushMe"
              style={logo}
            />
          </Section>

          {/* Title */}
          <Heading style={heading}>Thank you for your purchase!</Heading>

          {/* Greeting */}
          <Text style={text}>Hello {user_name},</Text>

          {/* Main message */}
          <Text style={text}>
            Your order has been confirmed and is being processed. We'll notify you when it's shipped.
          </Text>

          {/* Order information */}
          <Section style={orderInfoBox}>
            <Text style={orderLabel}>Order number</Text>
            <Text style={orderValue}>{order_number}</Text>
          </Section>

          {/* Products */}
          <Section style={productsSection}>
            <Text style={sectionTitle}>Products</Text>
            {items.map((item, index) => (
              <Row key={index} style={productRow}>
                <Column>
                  <Text style={productName}>{item.name}</Text>
                </Column>
                <Column align="right">
                  <Text style={productQuantity}>x{item.quantity}</Text>
                </Column>
              </Row>
            ))}
          </Section>

          <Hr style={divider} />

          {/* Total */}
          <Section style={totalsSection}>
            <Row style={totalRow}>
              <Column>
                <Text style={totalLabelBold}>Total</Text>
              </Column>
              <Column align="right">
                <Text style={totalValueBold}>${total.toLocaleString('en-US')}</Text>
              </Column>
            </Row>
          </Section>

          {/* Footer */}
          <Text style={footer}>
            If you have any questions about your order, don't hesitate to contact us.
          </Text>

          <Text style={footerSmall}>
            CrushMe · Medellín, Colombia
          </Text>
        </Container>
      </Body>
    </Html>
  );
};

const main = {
  backgroundColor: '#FFFFFF',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
};

const container = {
  margin: '0 auto',
  padding: '40px 20px',
  maxWidth: '600px',
};

const logoSection = {
  textAlign: 'center' as const,
  margin: '0 0 30px 0',
};

const logo = {
  margin: '0 auto',
};

const heading = {
  fontSize: '28px',
  fontWeight: '600',
  color: '#D689A2',
  textAlign: 'center' as const,
  margin: '0 0 30px 0',
  lineHeight: '1.3',
};

const text = {
  fontSize: '16px',
  color: '#4B5563',
  lineHeight: '1.6',
  margin: '0 0 20px 0',
};

const orderInfoBox = {
  backgroundColor: '#FAF3F3',
  padding: '24px',
  borderRadius: '12px',
  margin: '30px 0',
  textAlign: 'center' as const,
};

const orderLabel = {
  fontSize: '14px',
  color: '#6B7280',
  margin: '0 0 8px 0',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
};

const orderValue = {
  fontSize: '20px',
  color: '#11181E',
  fontWeight: '700',
  margin: '0',
};

const productsSection = {
  margin: '30px 0',
};

const sectionTitle = {
  fontSize: '18px',
  fontWeight: '600',
  color: '#11181E',
  margin: '0 0 20px 0',
};

const productRow = {
  margin: '0 0 16px 0',
};

const productName = {
  fontSize: '16px',
  color: '#4B5563',
  margin: '0',
};

const productQuantity = {
  fontSize: '16px',
  color: '#6B7280',
  margin: '0',
};

const divider = {
  borderColor: '#E5E7EB',
  margin: '30px 0',
};

const totalsSection = {
  margin: '30px 0',
};

const totalRow = {
  margin: '0 0 12px 0',
};

const totalLabelBold = {
  fontSize: '18px',
  fontWeight: '700',
  color: '#11181E',
  margin: '0',
};

const totalValueBold = {
  fontSize: '20px',
  fontWeight: '700',
  color: '#FF3FD5',
  margin: '0',
};

const footer = {
  fontSize: '14px',
  color: '#9CA3AF',
  textAlign: 'center' as const,
  margin: '40px 0 10px 0',
  paddingTop: '40px',
  borderTop: '1px solid #E5E7EB',
};

const footerSmall = {
  fontSize: '12px',
  color: '#D1D5DB',
  textAlign: 'center' as const,
  margin: '0',
};

OrderConfirmationEmail.PreviewProps = {
  user_name: 'Carlos',
  order_number: 'ORD-98765',
  total: 135500,
  items: [
    { name: 'CrushMe T-Shirt', quantity: 2 },
    { name: 'CrushMe Cap', quantity: 1 },
  ],
} as OrderConfirmationEmailProps;

export default OrderConfirmationEmail;
