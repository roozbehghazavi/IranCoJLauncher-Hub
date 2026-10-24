ParticleDef()
{
	LifeTime()
	{
		keyf(0.000000, 1.000000)
	}

	GravityMul()
	{
		keyf(0.000000, 0.300000)
	}

	Drag()
	{
		keyf(0.000000, 3.000000)
	}

	WindInfluence()
	{
		keyf(0.000000, 1.000000)
	}

	Color()
	{
		keyv4(0.002401, 0.354970, 0.358892, 0.358892, 0.997315)
		keyv4(0.254018, 0.777039, 0.780094, 0.781304, 0.919421)
		keyv4(0.538504, 0.892813, 0.892813, 0.892813, 0.094924)
		keyv4(0.999977, 0.974416, 0.980362, 0.980562, -0.105508)
	}

Size()
	{
		randf(-0.010494, 19.963238, 29.049000)
		randf(1.499361, 19.095433, 39.317087)
	}

	Rotation()
	{
		randf(-0.001692, 0.000000, 56.258041)
		randf(0.998308, 0.000000, 56.258041)
	}

	Material("bloodcircle_particleblend.mat", "bloodcircle_particleblend.mat")

	TexMultiRect(2, 1, 2)

	TexPlayMode("random_once", 1.000000)

}

