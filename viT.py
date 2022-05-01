import torch
import torch.nn as nn

class PatchEmbed(nn.Module):
    """
    split image into patches and then embed them

    Parameters
    ----------
    img_size: int
        size of the image (it is a square)
    patch_size: int 
        size of the patch (it is a square)
    in_channels : int
        number of input channels
    embed_dim: int
        The embedding dimension

    Attributes
    ----------
    n_patches: int
        Number of patches inside our image
    proj: nn.Conv2d
        Convulution layer that splits images into patches and embeds them
    
    """
    def __init__(self, img_size, patch_size, in_channels=3 , embed_dim=768):
        super(PatchEmbed, self).__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.n_patches = (img_size // patch_size) ** 2


        self.proj = nn.Conv2d(
            in_channels,
            embed_dim,
            kernel_size=patch_size,
            stride=patch_size
        )


    def forward(self, x):
        """
        Run Forward pass
        Parameters
        ----------
        x: torch.Tensor
            Shape '(n_samples, in_channels, img_size, img_size)'

        Returns
        -------
        torch.Tensor
            shape '(n_samples, n_patches, embed_dim)'
        """
        x = self.proj(x) # (n_samples, embed_dim, n_patches ** 0.5, n_patches 0.5)
        x = x.flatten(2) # (n_samples, embed_dim, n_patches)
        x = x.transpose(1, 2) # (n_samples, n_patches, embed_dim)

        return x

class SelfAttention(nn.Module):
    """
    Attention mechanism
    Paramters
    ---------
    dim: int
        The input and out dimension of per token features
    n_heads: int
        Number of attention heads
    qkv_bias: bool
        If true we include bias to the query, key and value projections
    attn_p: float
        Dropout probability applied to the query, key and value tensors
    proj_p: float
        Dropout probability applied to the output tensor

    Attributes
    ---------
    scale: float
        Normalizing constant for the dot product
    qkv: nn.Linear
        Linear projection for the query, key and value
    attn_drop, proj_drop: nn.Dropout
        Dropout layers
    """
    def __init__(self, dim, n_heads, qkv_bias =True, attn_p=0., proj_p=0.):
        super(SelfAttention, self).__init__()
        self.dim = dim
        self.heads = n_heads
        self.head_dim = dim // n_heads
        self.scale = self.head_dim ** -0.5

        assert (self.head_dim * n_heads == dim ), "Embed size needs to be divisble by heads"

        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_p)
        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_p)

    def forward(self, x):
        """
        Run forward pass

        Parameters
        ----------
        x : torch.Tensor
            Shape '(n_samples, n_patches + 1, dim)'

        Returns:
        torch.Tensor
            Shape '(n_samples, n_patches + 1, dim)'
        """
        n_samples, n_tokens, dim = x.shape

        if dim != self.dim:
            raise ValueError

        qkv = self.qkv(x) # (n_sammples, n_patches + 1, 3 * dim)
        qkv = qkv.reshape(n_samples, n_tokens, 3, self.heads, self.head_dim)

        qkv = qkv.permute(2, 0, 3, 1, 4) # (3, n_samples, n_heads, n_patches + 1, head_dim)
        query, keys, values = qkv[0], qkv[1], qkv[2]

        keys_t=keys.transpose(-2, -1) # (n_samples, n_heads, head_dim, n_patches + 1) 

        d_p = (query @ keys_t) * self.scale #(n_samples. n_headsn n_patches + 1, n_patches + 1)

        # if mask is not None:
        #     energy = energy.masked_fill(mask == 0, float("-1e20"))

        attention = d_p.softmax(dim=1)
        attention = self.attn_drop(attention)

        weighted_avg = attention @ values 
        weighted_avg=weighted_avg.transpose(1, 2) #(n_samples, n_patches+1, n_heads, head_dim)

        weighted_avg = weighted_avg.flatten(2) # (n_samples, n_patches + 1, dim)

        x = self.proj(weighted_avg) # (n_samples, n_patches + 1, dim)
        x = self.proj_drop(x) # (n_samples, n_patches + 1, dim)

        return x

class MLP(nn.Module):
    """
    Mulilayer Perceptron.

    Parameteres
    -----------
    in_features : int
        Number of input features
    hidden_features : int
        Number of nodes in the hidden layer
    out_features: int
        Number of output features
    p : float
        Dropout probability

    Attrubutes
    ----------
    fc1 : nn.Linear
        The first linear layer
    act : nn.GeLU
        GeLU activation function
    fc2 : nn.Linear
        The second linear layer
    """
    def __init__(self, in_features, hidden_features, out_features, p=0.):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_features, out_features)
        self.drop = nn.Dropout(p)


    def forward(self, x):
        """
        Run forward pass.

        Parameters
        ----------
        x : torch.Tensor
            shape '(n_samples, n_patches + 1, in_features)'

        Returns
        -------
        torch.Tensor
            shape '(n_samples, n_patches + 1, out_features)'
        """
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x

class Block(nn.Module):
    """
    Transformer block.

    Paramteres
    ----------
    dim : int
        Embedding dimension
    n_heads : int
        Number of attention heads
    mlp_ratio : float
        Determines the hidden dimension size of the MLP module with respect to 'dim'
    qkv_bias : bool
        If true, then we include bias to the query, key and value projections
    p, attn_p : float
        Dropout probability
    
    Attributes
    ----------
    norm1, norm2 : LayerNorm
        Layer Normalization
    attn : attention
        SelfAttention Module
    mlp : MLP 
        MLP module
    """
    def __init__(self, dim, n_heads, mlp_ratio=4.0, qkv_bias=True, p=0., attn_p=0.):
        super(Block, self).__init__()
        self.norm1 = nn.LayerNorm(dim, eps=1e-6)
        self.attn = SelfAttention(
            dim, 
            n_heads, 
            qkv_bias=qkv_bias, 
            attn_p=attn_p, 
            proj_p=p
        )
        self.norm2 = nn.LayerNorm(dim, eps=1e-6)
        hidden_features = int(dim * mlp_ratio)
        self.mlp = MLP(
            in_features = dim,
            hidden_features = hidden_features,
            out_features = dim
        )
    def forward(self, x):
        """
        Run forward pass.

        Parameters.
        -----------
        x  : torch.Tensor
         Shape "(n_samples, n_patches + 1, dim)".

        Returns:
        -------
        torch.Tensor
            Shape '(n_samples, n_patches + 1, dim)'.
        """
        x = x + self.attn(self.norm1(x))
        x = x + self.mlp(self.norm2(x))

        return x

class VisionTransformer(nn.Module):
    """
    Simplified implementation of the Vision Transformer
    
    Paramters:
    ---------
    img_size : int
        Both height and the width of the image(it is a square)
    patch_size : int
        Both height and the width of the image(it is a square)
    in_channels : int
        Number of input channels
    n_classes : int
        Number of classes
    embed_dim : int
        Dimensionality of the token/patch embeddings
    depth : int
        Number of Blocks
    n_heads: int
        Number of attention heads
    mlp_ratio : float
        Determines the hidden dimension of the 'MLP' module
    qkv_bias : bool
        If True, then we include bias to the query, key and value projections
    p, attn_p : float
        Dropout probability

    Attributes:
    -----------
    patch_embed : PatchEmbed
        Instance of 'PatchEmbed' layer
    cls_token : nn.Parameter
        Learnable parameter that will represent the first token in the sequence. It has 'embed_dim' elements
    pos_emb : nn_Parameter
        Positional embedding of the cls token + all the patches
        It has '(n_patches + 1) * embed_dim' elements
    pos_drop : nn.Dropout
        Dropout layer
    blocks : nn.ModuleList
        List of 'Block' Modules
    norm : nn.LayerNorm
        Layer normalization
    """
    def __init__(
        self, 
        img_size=384, 
        patch_size=16, 
        in_channels=3, 
        n_classes=1000, 
        embed_dim=768, 
        depth=12, 
        n_heads=12, 
        mlp_ratio = 4,
        qkv_bias=True,
        p=0.,
        attn_p=0.
    ):
        super(VisionTransformer, self).__init__()
        self.patch_embed = PatchEmbed(img_size=img_size, patch_size=patch_size, in_channels=in_channels, embed_dim=embed_dim)

        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, 1 + self.patch_embed.n_patches, embed_dim))

        self.pos_drop = nn.Dropout(p=p)
        self.blocks = nn.ModuleList(
            [
                Block(
                    dim=embed_dim,
                    n_heads=n_heads,
                    mlp_ratio=mlp_ratio,
                    qkv_bias=qkv_bias,
                    p=p,
                    attn_p=attn_p
                )
                for _ in range(depth)
            ]
        )
        self.norm = nn.LayerNorm(embed_dim, eps=1e-6)
        self.head = nn.Linear(embed_dim, n_classes)

    def forward(self, x):
        """
        Run the forward pass.

        Parameters
        ----------
        x : torch.Tensor
            Shape '(n_samples, in_channels, img_size, img_size)'

        Returns
        -------
        logits : torch.Tensor
            logits over all the classes - '(n_samples, n_classes)'.

        """
        n_samples = x.shape[0]
        x = self.patch_embed(x)

        cls_token = self.cls_token.expand(n_samples, -1, -1) # (n_samples, 1, embed_dim)
        x = torch.cat((cls_token, x), dim=1) # (n_samples, 1 + n_patches, embed_dim)
        x = x + self.pos_embed # (n_samples, 1 + n_patches, embed_dim)
        x = self.pos_drop(x)

        for block in self.blocks:
            x = block(x)
        
        x = self.norm(x)
        cls_token_final = x[:, 0]
        x = self.head(cls_token_final)

        return x



if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")