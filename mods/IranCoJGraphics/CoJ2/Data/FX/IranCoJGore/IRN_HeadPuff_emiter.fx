EmiterDef()
{
	LifeTime()
	{
		keyf(0, 0.5)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 3)
	}

	StartVelocity()
	{
		keyf(0, 380)
	}

	StartVelocityRand()
	{
		keyv(0, 240, 240, 240)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
